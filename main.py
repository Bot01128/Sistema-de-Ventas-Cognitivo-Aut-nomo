import os
import psycopg2
import json
import google.generativeai as genai
import uuid
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_babel import Babel
from cerebro_dashboard import create_chatbot
from werkzeug.routing import BaseConverter

# --- CONFIGURACION INICIAL ---
app = Flask(__name__)
# ¡IMPORTANTE! Se necesita una clave secreta para manejar las sesiones de forma segura
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "una-clave-secreta-muy-robusta-para-desarrollo")

# Conversor para UUID que faltaba en algunas versiones
class UUIDConverter(BaseConverter):
    def to_python(self, value):
        return uuid.UUID(value)
    def to_url(self, value):
        return str(value)
app.url_map.converters['uuid'] = UUIDConverter

# --- BLOQUE DE CONFIGURACION DE IDIOMAS (INTACTO) ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(basedir, 'translations')
def get_locale():
    if not request.accept_languages: return 'es'
    return request.accept_languages.best_match(['en', 'es'])
babel = Babel(app, locale_selector=get_locale)
@app.context_processor
def inject_get_locale():
    return dict(get_locale=get_locale)

# --- INICIALIZACION DE LA APLICACION Y BASE DE DATOS (INTACTO) ---
DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

print("=====================================================")
print(">>> [DIAGNOSTICO] INICIANDO APLICACION...")
if DATABASE_URL: print(">>> [DIAGNOSTICO] DATABASE_URL encontrada.")
else: print("!!! ERROR [DIAGNOSTICO]: DATABASE_URL NO FUE ENCONTRADA!")
print("=====================================================")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print(">>> [main.py] IA de Google configurada.")
else:
    print("!!! WARNING [main.py]: GOOGLE_API_KEY no encontrada.")

# --- CARGA DE LA PERSONALIDAD PARA EL CHAT (INTACTO) ---
ID_DE_LA_CAMPAÑA_ACTUAL = 1 
descripcion_de_la_campana = "Soy un asistente virtual generico, hubo un error al cargar la descripcion."
try:
    print(f">>> [main.py] Buscando descripcion para la campana ID: {ID_DE_LA_CAMPAÑA_ACTUAL}...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT descripcion_producto FROM campanas WHERE id = %s", (ID_DE_LA_CAMPAÑA_ACTUAL,))
    result = cur.fetchone()
    if result and result[0]:
        descripcion_de_la_campana = result[0]
        print(">>> [DIAGNOSTICO] EXITO! Se encontro la descripcion en Supabase.")
    else:
        print("!!! ERROR [DIAGNOSTICO]: Conexion exitosa, PERO NO SE ENCONTRO la campana con ID 1.")
    cur.close()
    conn.close()
except Exception as e:
    print(f"!!! ERROR FATAL [DIAGNOSTICO]: LA CONEXION A SUPABASE FALLO! El error fue: {e}")

dashboard_brain = create_chatbot(descripcion_producto=descripcion_de_la_campana)
if dashboard_brain:
    print(">>> [main.py] Cerebro con personalidad de campana inicializado.")
else:
    print("!!! ERROR [main.py]: El cerebro no pudo ser inicializado.")

# --- RUTAS DE LA APLICACION (CON LÓGICA DE AUTENTICACIÓN) ---

@app.route('/')
def home():
    # Esta ruta ahora solo redirige a la página de ventas.
    # El JavaScript se encargará de la lógica de sesión.
    return render_template('dashboard.html')

@app.route('/cliente')
def client_dashboard():
    # En el futuro, esta ruta estará protegida.
    return render_template('client_dashboard.html')

@app.route('/login')
def login():
    return render_template('login.html')
    
@app.route('/callback')
def callback():
    return render_template('callback.html')

@app.route('/chat', methods=['POST'])
def chat():
    if not dashboard_brain:
        return jsonify({"error": "Chat no disponible."}), 500
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No hay mensaje."}), 400
    try:
        response_text = dashboard_brain.invoke({"question": user_message})
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": "Ocurrio un error."}), 500

# --- (El resto de las rutas están intactas y correctas) ---
@app.route('/pre-nido/<uuid:id_unico>')
def mostrar_pre_nido(id_unico):
    nombre_negocio_db = "Empresa Real"
    return render_template('persuasor.html', prospecto_id=str(id_unico), nombre_negocio=nombre_negocio_db)

@app.route('/generar-nido', methods=['POST'])
def generar_nido_y_enviar_enlace():
    return render_template('nido_template.html')

@app.route('/ver-pre-nido')
def ver_pre_nido():
    id_de_prueba = str(uuid.uuid4())
    nombre_de_prueba = "Ferreteria El Tornillo Feliz (Prueba)"
    return render_template('persuasor.html', prospecto_id=id_de_prueba, nombre_negocio=nombre_de_prueba)

@app.route('/ver-nido')
def ver_nido():
    return render_template('nido_template.html')

# --- BLOQUE DE ARRANQUE ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
