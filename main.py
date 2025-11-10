import os
import psycopg2
import json
import google.generativeai as genai
# SE AÑADE 'send_from_directory' PARA SERVIR ARCHIVOS ESTÁTICOS DESDE 'persuador'
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_babel import Babel, gettext
from cerebro_dashboard import create_chatbot

# --- NO TOCAMOS LAS IMPORTACIONES ---
from trabajador_orquestador import orquestar_nueva_caza
from trabajador_cazador import cazar_prospectos

# --- CONFIGURACIÓN (INTACTA) ---
app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
ID_DE_LA_CAMPAÑA_ACTUAL = 1 
descripcion_de_la_campana = "Soy un asistente virtual genérico."
try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT descripcion_producto FROM campanas WHERE id = %s", (ID_DE_LA_CAMPAÑA_ACTUAL,))
    result = cur.fetchone()
    if result and result[0]:
        descripcion_de_la_campana = result[0]
    cur.close()
    conn.close()
except Exception:
    pass 
dashboard_brain = create_chatbot(descripcion_producto=descripcion_de_la_campana)

def get_locale():
    return request.accept_languages.best_match(['en', 'es'])

babel = Babel(app, locale_selector=get_locale)

@app.context_processor
def inject_global_funcs():
    return dict(get_locale=get_locale, _=gettext)


# --- RUTAS DE LA APLICACIÓN ---

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/generar-nido')
def generar_nido_page():
    return render_template('nido_template.html')

# ======================= LA SOLUCIÓN DEFINITIVA =======================
# RUTA PARA LA PÁGINA DE CHAT INTERACTIVO (AHORA SIMPLIFICADA)
@app.route('/pre-nido')
def pre_nido_page():
    # Simplemente muestra el archivo HTML. No necesita nada más.
    return render_template('persuador/pre_nido.html')

# NUEVA RUTA ESPECIAL PARA SERVIR CSS Y JS DESDE LA CARPETA 'persuador'
@app.route('/persuador/<path:filename>')
def serve_persuador_files(filename):
    # Esta función intercepta cualquier petición a /persuador/...
    # y sirve el archivo correspondiente desde el directorio 'persuador'.
    return send_from_directory('persuador', filename)
# =====================================================================


@app.route('/chat', methods=['POST'])
def chat():
    # ... código intacto ...
    if not dashboard_brain: return jsonify({"error": "Chat no disponible."}), 500
    user_message = request.json.get('message')
    if not user_message: return jsonify({"error": "No hay mensaje."}), 400
    try:
        response_text = dashboard_brain.invoke({"question": user_message})
        return jsonify({"response": response_text})
    except Exception as e: return jsonify({"error": "Ocurrió un error."}), 500

@app.route('/lanzar-campana', methods=['POST'])
def lanzar_campana():
    # ... código intacto ...
    print("\n>>> [RUTA /lanzar-campana] ¡Orden recibida del Dashboard!")
    orden_del_cliente = request.get_json()
    if not orden_del_cliente:
        return jsonify({"error": "No se recibieron datos de la campaña."}), 400
    conn = None
    try:
        print(">>> [RUTA /lanzar-campana] Dejando la orden en la 'cola_de_trabajos'...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        sql_insert = "INSERT INTO cola_de_trabajos (tipo_trabajo, datos_json) VALUES (%s, %s);"
        datos_como_texto_json = json.dumps(orden_del_cliente)
        cur.execute(sql_insert, ('cazar_prospectos', datos_como_texto_json))
        conn.commit()
        print(">>> [RUTA /lanzar-campana] ¡Orden dejada en el buzón con éxito!")
        return jsonify({"message": "¡Campaña recibida! Hemos empezado a trabajar en ello. Te notificaremos cuando los prospectos estén listos."})
    except Exception as e:
        print(f"!!! ERROR FATAL en /lanzar-campana: {e}")
        return jsonify({"error": f"Ocurrió un error en el servidor al encolar el trabajo: {e}"}), 500
    finally:
        if conn:
            conn.close()

# --- BLOQUE DE ARRANQUE (INTACTO) ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
