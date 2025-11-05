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

# --- INICIALIZACIÓN DEL CEREBRO ---
dashboard_brain = create_chatbot()
if dashboard_brain:
    print(">>> [main.py] Cerebro con memoria inicializado.")

# --- CONFIGURACIÓN DE IDIOMA ---
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
        return jsonify({"error": "Cerebro no disponible."}), 500
    
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No hay mensaje."}), 400
        
    try:
        response = dashboard_brain.invoke({"question": user_message})
        return jsonify({"response": response})
    except Exception as e:
        print(f"!!! ERROR al procesar chat: {e} !!!")
        return jsonify({"error": "Ocurrió un error."}), 500

# --- TUS RUTAS ORIGINALES, INTACTAS ---
@app.route('/test-nido')
def test_nido():
    # ... (Tu código de test-nido original va aquí) ...
    pass

@app.route('/pre-nido/<uuid:id_unico>')
def mostrar_pre_nido(id_unico):
    # ... (Tu código de pre-nido original va aquí) ...
    pass

@app.route('/generar-nido', methods=['POST'])
def generar_nido_y_enviar_enlace():
    # ... (Tu código de generar-nido original va aquí) ...
    pass

# --- BLOQUE DE ARRANQUE ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
