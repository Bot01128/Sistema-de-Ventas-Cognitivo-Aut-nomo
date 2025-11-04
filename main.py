import os
from flask import Flask, render_template, request, jsonify
from flask_babel import Babel
import google.generativeai as genai
from cerebro_dashboard import create_dashboard_brain

app = Flask(__name__)
# ... (Tu configuración original de Babel, etc.) ...

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print(">>> [Main] IA de Google configurada.")

dashboard_brain = create_dashboard_brain()

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
# ... (El resto de TUS rutas originales, intactas) ...
