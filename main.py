# main.py (está bien, no necesitas cambiarlo)
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
    print(">>> [main.py] IA de Google configurada.")
else:
    print("!!! WARNING [main.py]: GOOGLE_API_KEY no encontrada.")

# --- INICIALIZACIÓN DEL CEREBRO ---
dashboard_brain = create_chatbot()
if dashboard_brain:
    print(">>> [main.py] Cerebro con memoria inicializado.")
else:
    print("!!! ERROR [main.py]: El cerebro no pudo ser inicializado.")


# --- CONFIGURACIÓN DE IDIOMA (Tu código está bien) ---
def get_locale():
    if not request.accept_languages:
        return 'es'
    return request.accept_languages.best_match(['en', 'es'])

babel = Babel(app, locale_selector=get_locale)
app.jinja_env.globals.update(get_locale=get_locale)


# --- RUTAS DE LA APLICACIÓN ---

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

# --- BLOQUE DE ARRANQUE ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
