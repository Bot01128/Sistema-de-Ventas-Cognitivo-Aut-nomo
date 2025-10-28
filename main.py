from flask import Flask, render_template, request, jsonify
from flask_babel import Babel
import os
from cerebro_dashboard import create_dashboard_brain

app = Flask(__name__)

def get_locale():
    # Asegurémonos de tener un valor predeterminado si accept_languages está vacío
    if not request.accept_languages:
        return 'es'
    return request.accept_languages.best_match(['en', 'es'])

babel = Babel(app, locale_selector=get_locale)
app.jinja_env.globals.update(get_locale=get_locale)

# --- CEREBRO DEL DASHBOARD EXISTENTE ---
dashboard_brain = create_dashboard_brain()

# --- RUTA PRINCIPAL (TU DASHBOARD) ---
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# --- RUTA DE CHAT PARA EL DASHBOARD ---
@app.route('/chat', methods=['POST'])
def chat():
    if not dashboard_brain:
        return jsonify({"error": "Cerebro no disponible."}), 500

    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No hay mensaje."}), 400

    print(f"--- Mensaje chat: '{user_message}' ---")
    
    try:
        response = dashboard_brain.invoke({"question": user_message})
        print(f"--- Respuesta IA: '{response}' ---")
        
        return jsonify({"response": response})
    except Exception as e:
        print(f"!!! ERROR al procesar chat: {e} !!!")
        return jsonify({"error": "Ocurrió un error al procesar."}), 500

# --- NUEVA RUTA DE PRUEBA PARA EL NIDO DE CONVERSIÓN ---
@app.route('/test-nido')
def test_nido():
    # Datos de prueba para rellenar la plantilla
    datos_de_prueba = {
        "nombre_negocio": "Ferretería El Tornillo Feliz",
        "titulo_personalizado": "Diagnóstico y Oportunidades para Ferretería El Tornillo Feliz",
        "texto_diagnostico": "Hemos detectado que su sitio web actual no ofrece a los clientes una forma inmediata de contacto, como un chat en vivo, lo que podría estar causando la pérdida de clientes impacientes.",
        "ejemplo_pregunta_1": "¿Tienen stock de taladros inalámbricos DeWalt?",
        "ejemplo_respuesta_1": "¡Claro que sí! Tenemos el modelo DCD777C2 a $120.00. Incluye 2 baterías y cargador. ¿Le gustaría que le reservemos uno?",
        "ejemplo_pregunta_2": "¿Hasta qué hora están abiertos hoy?",
        "ejemplo_respuesta_2": "Hoy estamos abiertos hasta las 6:00 PM. ¡Lo esperamos!",
        "texto_contenido_de_valor": "Un Agente de IA no solo responde preguntas, también puede capturar los datos de contacto de clientes potenciales fuera de horario, asegurando que ninguna oportunidad de venta se pierda."
    }
    # La doble estrella (**) "desempaqueta" el diccionario para pasarlo a la plantilla
    return render_template('nido_template.html', **datos_de_prueba)


# --- BLOQUE DE ARRANQUE DEL SERVIDOR ---
if __name__ == '__main__':
    # Usamos el puerto que Render nos da, con un valor por defecto de 8080 para pruebas locales
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
