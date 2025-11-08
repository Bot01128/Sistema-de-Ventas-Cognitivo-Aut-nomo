import os
import psycopg2
import json
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from flask_babel import Babel
from cerebro_dashboard import create_chatbot

# --- CONFIGURACIÓN INICIAL ---
app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# --- CÁMARA DE DIAGNÓSTICO #1 ---
print("=====================================================")
print(">>> [DIAGNÓSTICO] INICIANDO APLICACIÓN...")
if DATABASE_URL:
    # Imprimimos solo una parte para no exponer la contraseña completa en los logs
    print(">>> [DIAGNÓSTICO] DATABASE_URL encontrada. Comienza con:", DATABASE_URL[:30]) 
else:
    print("!!! ERROR [DIAGNÓSTICO]: ¡DATABASE_URL NO FUE ENCONTRADA EN LAS VARIABLES DE ENTORNO!")
print("=====================================================")


# Configurar la IA de Google globalmente
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print(">>> [main.py] IA de Google configurada.!!!")
else:
    print("!!! WARNING [main.py]: GOOGLE_API_KEY no encontrada.")

# --- INICIO DE LA NUEVA LÓGICA ---

# --- CARGA DE LA PERSONALIDAD DE LA CAMPAÑA ---
# SIMULACIÓN: Estamos trabajando con la campaña con id = 1.
ID_DE_LA_CAMPAÑA_ACTUAL = 1 
descripcion_de_la_campana = "Soy un asistente virtual genérico, hubo un error al cargar la descripción."

try:
    print(f">>> [main.py] Buscando descripción para la campaña ID: {ID_DE_LA_CAMPAÑA_ACTUAL}...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT descripcion_producto FROM campanas WHERE id = %s", (ID_DE_LA_CAMPAÑA_ACTUAL,))
    result = cur.fetchone()

    # --- CÁMARA DE DIAGNÓSTICO #2 ---
    if result and result[0]:
        descripcion_de_la_campana = result[0]
        print(">>> [DIAGNÓSTICO] ¡ÉXITO! Se encontró la siguiente descripción en Supabase:")
        print(descripcion_de_la_campana)
    else:
        print("!!! ERROR [DIAGNÓSTICO]: La conexión a Supabase funcionó, PERO NO SE ENCONTRÓ la campaña con ID 1.")
    
    cur.close()
    conn.close()
except Exception as e:
    print("!!! ERROR FATAL [DIAGNÓSTICO]: ¡LA CONEXIÓN A SUPABASE FALLÓ! El error fue:")
    print(e)

# --- INICIALIZACIÓN DEL CEREBRO (AHORA CON PERSONALIDAD) ---
dashboard_brain = create_chatbot(descripcion_producto=descripcion_de_la_campana)

if dashboard_brain:
    print(">>> [main.py] Cerebro con personalidad de campaña inicializado.")
else:
    print("!!! ERROR [main.py]: El cerebro no pudo ser inicializado.")

# --- FIN DE LA NUEVA LÓGICA ---


# --- CONFIGURACIÓN DE IDIOMA (Tu código intacto) ---
def get_locale():
    if not request.accept_languages:
        return 'es'
    return request.accept_languages.best_match(['en', 'es'])

babel = Babel(app, locale_selector=get_locale)
app.jinja_env.globals.update(get_locale=get_locale)


# --- RUTAS DE LA APLICACIÓN (Tu código intacto) ---
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/chat', methods=['POST'])
def chat():
    if not dashboard_brain:
        print("!!! ERROR [/chat]: Intento de chat con cerebro no inicializado.")
        return jsonify({"error": "El servicio de chat no está disponible en este momento. Revisa los logs del servidor."}), 500
    
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No se recibió ningún mensaje en la solicitud."}), 400
        
    try:
        # La llamada a invoke() sigue funcionando igual
        response_text = dashboard_brain.invoke({"question": user_message})
        return jsonify({"response": response_text})
    except Exception as e:
        print(f"!!! ERROR fatal en la ruta /chat: {e} !!!")
        return jsonify({"error": "Ocurrió un error inesperado al procesar el mensaje."}), 500

# --- RUTAS ORIGINALES DEL PROYECTO NIDO (RESTAURADAS) ---
@app.route('/test-nido')
def test_nido():
    return "Ruta de prueba para Nido funcionando."

@app.route('/pre-nido/<uuid:id_unico>')
def mostrar_pre_nido(id_unico):
    return render_template('pre_nido.html', id_unico=id_unico)

@app.route('/generar-nido', methods=['POST'])
def generar_nido_y_enviar_enlace():
    return "Ruta para generar-nido funcionando (solo POST)."


# --- BLOQUE DE ARRANQUE (Tu código intacto) ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
