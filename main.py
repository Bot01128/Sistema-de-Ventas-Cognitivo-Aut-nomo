import os
import psycopg2
import json
import google.generativeai as genai
import uuid
from flask import Flask, render_template, request, jsonify
from flask_babel import Babel
from cerebro_dashboard import create_chatbot

# --- CONFIGURACIÓN INICIAL ---
app = Flask(__name__)

# --- BLOQUE DE CONFIGURACIÓN DE IDIOMAS (VERSIÓN FINAL Y CORRECTA) ---

# 1. Le damos la dirección GPS exacta a la carpeta de traducciones
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(basedir, 'translations')

# 2. Definimos la función para detectar el idioma
def get_locale():
    return request.accept_languages.best_match(['en', 'es'])

# 3. Inicializamos Babel usando el método compatible
babel = Babel(app, locale_selector=get_locale)

# 4. ¡¡¡====== ESTA ES LA CORRECCIÓN MÁGICA Y PROFESIONAL ======!!!
# Usamos un "Context Processor" para darle de forma segura la herramienta 
# get_locale() a TODOS los archivos HTML. Este es el método correcto.
@app.context_processor
def inject_get_locale():
    return dict(get_locale=get_locale)
# ¡¡¡=============================================================!!!


# --- (EL RESTO DE TU CÓDIGO ESTÁ 100% INTACTO) ---
DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

print("=====================================================")
print(">>> [DIAGNÓSTICO] INICIANDO APLICACIÓN...")
if DATABASE_URL:
    print(">>> [DIAGNÓSTICO] DATABASE_URL encontrada. Comienza con:", DATABASE_URL[:30])
else:
    print("!!! ERROR [DIAGNÓSTICO]: ¡DATABASE_URL NO FUE ENCONTRADA EN LAS VARIABLES DE ENTORNO!")
print("=====================================================")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print(">>> [main.py] IA de Google configurada.!!!")
else:
    print("!!! WARNING [main.py]: GOOGLE_API_KEY no encontrada.")
ID_DE_LA_CAMPAÑA_ACTUAL = 1
descripcion_de_la_campana = "Soy un asistente virtual genérico, hubo un error al cargar la descripción."
try:
    print(f">>> [main.py] Buscando descripción para la campaña ID: {ID_DE_LA_CAMPAÑA_ACTUAL}...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT descripcion_producto FROM campanas WHERE id = %s", (ID_DE_LA_CAMPAÑA_ACTUAL,))
    result = cur.fetchone()
    if result and result[0]:
        descripcion_de_la_campana = result[0]
        print(">>> [DIAGNÓSTICO] ¡ÉXITO! Se encontró la descripción en Supabase.")
    else:
        print("!!! ERROR [DIAGNÓSTICO]: La conexión a Supabase funcionó, PERO NO SE ENCONTRÓ la campaña con ID 1.")
    cur.close()
    conn.close()
except Exception as e:
    print(f"!!! ERROR FATAL [DIAGNÓSTICO]: ¡LA CONEXIÓN A SUPABASE FALLÓ! El error fue:")
    print(e)
dashboard_brain = create_chatbot(descripcion_producto=descripcion_de_la_campana)
if dashboard_brain:
    print(">>> [main.py] Cerebro con personalidad de campaña inicializado.")
else:
    print("!!! ERROR [main.py]: El cerebro no pudo ser inicializado.")

# --- RUTAS DE LA APLICACIÓN (INTACTAS) ---
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

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
        return jsonify({"error": "Ocurrió un error."}), 500

# --- RUTAS DEL PERSUASOR (INTACTAS) ---
@app.route('/pre-nido/<uuid:id_unico>')
def mostrar_pre_nido(id_unico):
    nombre_negocio_db = "Empresa Real"
    textos_db = {}
    return render_template('persuasor.html',
                           prospecto_id=str(id_unico),
                           nombre_negocio=nombre_negocio_db,
                           textos=textos_db)

@app.route('/generar-nido', methods=['POST'])
def generar_nido_y_enviar_enlace():
    return render_template('nido_template.html')

# --- RUTAS DE PRUEBA (INTACTAS) ---
@app.route('/ver-pre-nido')
def ver_pre_nido():
    id_de_prueba = str(uuid.uuid4())
    nombre_de_prueba = "Ferretería El Tornillo Feliz (Prueba)"
    return render_template('persuasor.html',
                           prospecto_id=id_de_prueba,
                           nombre_negocio=nombre_de_prueba,
                           textos={})

@app.route('/ver-nido')
def ver_nido():
    return render_template('nido_template.html')

# --- BLOQUE DE ARRANQUE (INTACTO) ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
