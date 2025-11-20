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
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")

# --- CARGA DE LA PERSONALIDAD PARA EL CHAT ---
dashboard_brain = None
try:
    print("=====================================================")
    print(">>> [DIAGNOSTICO] INICIANDO APLICACION...")
    if DATABASE_URL: print(">>> [DIAGNOSTICO] DATABASE_URL encontrada.")
    else: print("!!! ERROR [DIAGNOSTICO]: DATABASE_URL NO FUE ENCONTRADA!")
    if GOOGLE_API_KEY: print(">>> [main.py] GOOGLE_API_KEY encontrada.")
    else: print("!!! WARNING [main.py]: GOOGLE_API_KEY no encontrada.")
    print("=====================================================")

    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
        
    ID_DE_LA_CAMPAÑA_ACTUAL = 1 
    descripcion_de_la_campana = "Soy un asistente virtual generico, hubo un error al cargar la descripcion."
    
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
    
    dashboard_brain = create_chatbot(descripcion_producto=descripcion_de_la_campana)
    if dashboard_brain:
        print(">>> [main.py] Cerebro con personalidad de campana inicializado.")
    else:
        print("!!! ERROR [main.py]: El cerebro no pudo ser inicializado.")

except Exception as e:
    print(f"!!! ERROR FATAL [DIAGNOSTICO]: Fallo en la inicializacion. El error fue: {e}")

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
    if not dashboard_brain: return jsonify({"error": "Chat no disponible por error de inicializacion."}), 500
    user_message = request.json.get('message')
    if not user_message: return jsonify({"error": "No hay mensaje."}), 400
    try:
        response_text = dashboard_brain.invoke({"question": user_message})
        return jsonify({"response": response_text})
    except Exception as e: return jsonify({"error": f"Ocurrio un error en el chat: {e}"}), 500

# --- RUTAS DEL PERSUASOR ---
@app.route('/pre-nido/<uuid:id_unico>')
def mostrar_pre_nido(id_unico):
    nombre_negocio_db = "Empresa Real"
    return render_template('persuasor.html', prospecto_id=str(id_unico), nombre_negocio=nombre_negocio_db)

# === INICIO DE LA ÚNICA MODIFICACIÓN: LÓGICA DE CAPTURA DE EMAIL AÑADIDA ===
@app.route('/generar-nido', methods=['POST'])
def generar_nido_y_enviar_enlace():
    # 1. Recibir los datos del formulario de la página 'persuasor.html'
    email = request.form.get('email')
    prospecto_id = request.form.get('prospecto_id')

    # 2. Validar que recibimos los datos necesarios antes de proceder
    if email and prospecto_id:
        conn = None
        try:
            # 3. Conectarse a la base de datos para actualizar al prospecto
            print(f">>> [main.py] Recibido email: '{email}' para prospecto ID: {prospecto_id}. Actualizando DB...")
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            
            # 4. Preparar y ejecutar la actualización del prospecto
            nuevo_estado = 'email_capturado'
            cur.execute(
                "UPDATE prospectos SET email = %s, estado_prospecto = %s WHERE id = %s",
                (email, nuevo_estado, prospecto_id)
            )
            
            # 5. Confirmar y guardar los cambios en la base de datos
            conn.commit()
            print(f">>> [DIAGNOSTICO] EXITO! Prospecto {prospecto_id} actualizado a estado '{nuevo_estado}'.")

        except Exception as e:
            # 6. En caso de error, imprimirlo y deshacer cualquier cambio
            print(f"!!! ERROR [DIAGNOSTICO]: No se pudo actualizar el prospecto {prospecto_id}. Error: {e}")
            if conn:
                conn.rollback()
        
        finally:
            # 7. Asegurarse de cerrar siempre la conexión a la base de datos
            if conn:
                cur.close()
                conn.close()
    else:
        # Mensaje de advertencia si no se reciben los datos esperados
        print("!!! WARNING [main.py]: No se recibieron email o prospecto_id en /generar-nido.")

    # 8. Finalmente, mostrar la página 'nido_template.html' como lo hacía antes
    return render_template('nido_template.html')
# === FIN DE LA ÚNICA MODIFICACIÓN ===


# --- RUTAS DE PRUEBA ---
@app.route('/ver-pre-nido')
def ver_pre_nido():
    id_de_prueba = str(uuid.uuid4())
    nombre_de_prueba = "Ferreteria El Tornillo Feliz (Prueba)"
    return render_template('persuasor.html', prospecto_id=id_de_prueba, nombre_de_prueba)

@app.route('/ver-nido')
def ver_nido():
    return render_template('nido_template.html')

# --- BLOQUE DE ARRANQUE ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
