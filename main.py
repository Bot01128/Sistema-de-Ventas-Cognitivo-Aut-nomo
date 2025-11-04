import os
from flask import Flask, render_template, request, jsonify
from flask_babel import Babel
import google.generativeai as genai
# --- ¡NUEVAS IMPORTACIONES! ---
# Importamos el cerebro trasplantado desde su nueva carpeta
from bot_de_respuesta.cerebro import create_chatbot

# --- CONFIGURACIÓN INICIAL ---
app = Flask(__name__)
# ... (Tu configuración de Babel y otras variables) ...

# Configurar la IA de Google globalmente (¡CRÍTICO!)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print(">>> [main.py] IA de Google configurada.")
else:
    print("!!! ADVERTENCIA: GOOGLE_API_KEY no encontrada.")

# --- INICIALIZACIÓN DEL NUEVO CEREBRO ---
dashboard_brain = create_chatbot()

# --- RUTAS DE LA APLICACIÓN ---
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# --- ¡RUTA DE CHAT ADAPTADA PARA EL NUEVO CEREBRO! ---
@app.route('/chat', methods=['POST'])
def chat():
    if not dashboard_brain:
        return jsonify({"error": "Cerebro no disponible."}), 500
    
    user_message = request.json.get('message')
    # Usaremos una session_id fija para probar, luego la haremos dinámica
    session_id = "test_session_dashboard" 
    
    if not user_message:
        return jsonify({"error": "No hay mensaje."}), 400
        
    try:
        print(f"--- [main.py] Invocando cerebro con: '{user_message}' para session_id: {session_id} ---")
        
        # Usamos la estructura que espera el nuevo cerebro
        response_object = dashboard_brain.invoke(
            {"input": user_message},
            config={"configurable": {"session_id": session_id}}
        )
        
        # Extraemos el contenido de la respuesta
        ai_response = response_object.content
        
        print(f"--- [main.py] Respuesta recibida: '{ai_response}' ---")
        return jsonify({"response": ai_response})

    except Exception as e:
        print(f"!!! ERROR al procesar chat con el nuevo cerebro: {e} !!!")
        return jsonify({"error": "Ocurrió un error al procesar la respuesta."}), 500

# ... (El resto de tus rutas, como /crear-campana, /nido-template, etc., van aquí sin cambios) ...

# --- BLOQUE DE ARRANQUE ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
