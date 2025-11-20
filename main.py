import os
import psycopg2
import json
import google.generativeai as genai
import uuid
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_babel import Babel
from cerebro_dashboard import create_chatbot
from werkzeug.routing import BaseConverter

# --- CONFIGURACION INICIAL ---
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "una-clave-secreta-muy-robusta-para-desarrollo")
class UUIDConverter(BaseConverter):
    def to_python(self, value): return uuid.UUID(value)
    def to_url(self, value): return str(value)
app.url_map.converters['uuid'] = UUIDConverter

# --- BLOQUE DE CONFIGURACION DE IDIOMAS ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(basedir, 'translations')
def get_locale():
    if not request.accept_languages: return 'es'
    return request.accept_languages.best_match(['en', 'es'])
babel = Babel(app, locale_selector=get_locale)
@app.context_processor
def inject_get_locale():
    return dict(get_locale=get_locale)

# --- INICIALIZACION DE LA APLICACION Y BASE DE DATOS ---
DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# === LA SOLUCIÓN DEFINITIVA: CARGA PEREZOSA (LAZY LOADING) ===
# El cerebro de la IA se inicializa como 'None'. No se cargará al arrancar.
dashboard_brain = None
# Configuramos la API de Google una sola vez si la clave existe.
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
# === FIN DE LA MODIFICACIÓN ESTRUCTURAL ===

# --- RUTA DE HEALTHCHECK PARA RAILWAY ---
@app.route('/health')
def health_check():
    # Esta ruta es usada por la plataforma para verificar que la app está viva.
    # Es instantánea porque ya no depende de la carga de la IA.
    return "OK", 200

# --- RUTAS DE LA APLICACION ---
@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/cliente')
def client_dashboard():
    return render_template('client_dashboard.html')

@app.route('/mis-clientes')
def mis_clientes():
    return render_template('mis_clientes.html')

@app.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/taller')
def admin_taller():
    return render_template('admin_taller.html')

@app.route('/chat', methods=['POST'])
def chat():
    global dashboard_brain # Usamos la variable global

    try:
        # === INICIO DE LA CARGA PEREZOSA ===
        # Si el cerebro es 'None', significa que es el PRIMER mensaje de chat.
        # Solo en este caso, realizamos la operación lenta de cargar la IA.
        if dashboard_brain is None:
            print(">>> [main.py - LAZY LOADING] Primer mensaje de chat recibido. INICIALIZANDO CEREBRO...")
            ID_DE_LA_CAMPAÑA_ACTUAL = 1 
            descripcion_de_la_campana = "Soy un asistente virtual generico, hubo un error al cargar la descripcion."
            
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute("SELECT descripcion_producto FROM campanas WHERE id = %s", (ID_DE_LA_CAMPAÑA_ACTUAL,))
            result = cur.fetchone()
            if result and result[0]:
                descripcion_de_la_campana = result[0]
            cur.close()
            conn.close()
            
            dashboard_brain = create_chatbot(descripcion_producto=descripcion_de_la_campana)
            print(">>> [main.py - LAZY LOADING] Cerebro inicializado y listo para reusar.")
        # === FIN DE LA CARGA PEREZOSA ===

        user_message = request.json.get('message')
        if not user_message: return jsonify({"error": "No hay mensaje."}), 400
        
        response_text = dashboard_brain.invoke({"question": user_message})
        return jsonify({"response": response_text})

    except Exception as e:
        print(f"!!! ERROR FATAL en la ruta /chat: {e}")
        return jsonify({"error": f"Ocurrio un error en el chat: {e}"}), 500

# --- RUTAS DEL PERSUASOR ---
@app.route('/pre-nido/<uuid:id_unico>')
def mostrar_pre_nido(id_unico):
    nombre_negocio_db = "Empresa Real"
    return render_template('persuasor.html', prospecto_id=str(id_unico), nombre_negocio=nombre_negocio_db)

@app.route('/generar-nido', methods=['POST'])
def generar_nido_y_enviar_enlace():
    email = request.form.get('email')
    prospecto_id = request.form.get('prospecto_id')
    if email and prospecto_id:
        conn = None
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            nuevo_estado = 'email_capturado'
            cur.execute(
                "UPDATE prospectos SET email = %s, estado_prospecto = %s WHERE id = %s",
                (email, nuevo_estado, prospecto_id)
            )
            conn.commit()
        except Exception as e:
            if conn: conn.rollback()
        finally:
            if conn:
                cur.close()
                conn.close()
    return render_template('nido_template.html')

# --- RUTAS DE PRUEBA ---
@app.route('/ver-pre-nido')
def ver_pre_nido():
    id_real_para_prueba = "1"
    nombre_de_prueba = "Ferreteria El Tornillo Feliz (Prueba)"
    return render_template('persuasor.html', prospecto_id=id_real_para_prueba, nombre_negocio=nombre_de_prueba)

@app.route('/ver-nido')
def ver_nido():
    return render_template('nido_template.html')

# --- BLOQUE DE ARRANQUE ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
