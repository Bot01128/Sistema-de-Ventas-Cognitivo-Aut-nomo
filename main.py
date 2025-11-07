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
    if result and result[0]:
        descripcion_de_la_campana = result[0]
        print(">>> [main.py] ¡Descripción encontrada en Supabase!")
    else:
        print("!!! WARNING [main.py]: No se encontró descripción para esa campaña. Usando descripción por defecto.")
    cur.close()
    conn.close()
except Exception as e:
    print(f"!!! ERROR [main.py]: No se pudo leer la descripción desde Supabase. {e}")

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

# --- TUS OTRAS RUTAS (No las toques) ---


# --- BLOQUE DE ARRANQUE (Tu código intacto) ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
