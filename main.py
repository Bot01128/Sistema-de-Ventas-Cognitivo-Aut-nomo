from flask import Flask, render_template, request, jsonify
from flask_babel import Babel
import os
# ¡Importamos nuestro nuevo cerebro!
from cerebro_dashboard import create_dashboard_brain

app = Flask(__name__)

# --- Configuración de Babel ---
def get_locale():
    return request.accept_languages.best_match(['en', 'es'])

babel = Babel(app, locale_selector=get_locale)
app.jinja_env.globals.update(get_locale=get_locale)

# --- Inicializamos el Cerebro del Dashboard ---
dashboard_brain = create_dashboard_brain()

# --- Rutas de la Aplicación ---
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# --- NUEVA RUTA PARA MANEJAR EL CHAT ---
@app.route('/chat', methods=['POST'])
def chat():
    if not dashboard_brain:
        return jsonify({"error": "El cerebro de la IA no está disponible."}), 500

    # Obtenemos la pregunta del usuario desde el frontend
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No se recibió ningún mensaje."}), 400

    print(f"--- Mensaje recibido en el chat: '{user_message}' ---")
    
    try:
        # Le pasamos la pregunta al cerebro
        response = dashboard_brain.predict(question=user_message)
        print(f"--- Respuesta generada por la IA: '{response}' ---")
        
        # Devolvemos la respuesta al frontend
        return jsonify({"response": response})
    except Exception as e:
        print(f"!!! ERROR al procesar el mensaje del chat: {e} !!!")
        return jsonify({"error": "Ocurrió un error al procesar tu mensaje."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
