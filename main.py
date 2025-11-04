import os
import psycopg2
import json
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from flask_babel import Babel
# ¡LA IMPORTACIÓN CLAVE!
# Ahora apuntamos al cerebro_dashboard.py que reemplazaremos
from cerebro_dashboard import create_chatbot

# --- CONFIGURACIÓN INICIAL ---
app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Configurar la IA de Google globalmente (CRÍTICO)
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print(">>> [main.py] IA de Google configurada exitosamente.")
else:
    print("!!! ADVERTENCIA: [main.py] GOOGLE_API_KEY no encontrada.")

# --- INICIALIZACIÓN DEL CEREBRO ---
# Llamamos a la función que crea nuestro nuevo cerebro con memoria
dashboard_brain = create_chatbot()
if dashboard_brain:
    print(">>> [main.py] Cerebro con memoria inicializado con éxito.")
else:
    print("!!! ERROR CRÍTICO: [main.py] No se pudo inicializar el cerebro del chat.")

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

# --- ¡¡¡RUTA DE CHAT CON LA LÓGICA DEL BOT DE FACEBOOK!!! ---
@app.route('/chat', methods=['POST'])
def chat():
    if not dashboard_brain:
        return jsonify({"error": "El cerebro del chat no está funcionando."}), 500
    
    data = request.get_json()
    user_message = data.get('message')
    # Usamos un ID de sesión estático para el dashboard
    session_id = "dashboard_user_session" 
    
    if not user_message:
        return jsonify({"error": "No se recibió ningún mensaje."}), 400
        
    try:
        print(f"--- [main.py] Invocando cerebro con: '{user_message}' (Sesión: {session_id}) ---")
        
        # Usamos la lógica de invoke con session_id
        response_object = dashboard_brain.invoke(
            {"input": user_message},
            config={"configurable": {"session_id": session_id}}
        )
        
        ai_response = response_object.content
        
        print(f"--- [main.py] Respuesta del cerebro: '{ai_response}' ---")
        return jsonify({"response": ai_response})

    except Exception as e:
        print(f"!!! ERROR [main.py] al procesar el chat: {e} !!!")
        return jsonify({"error": "Ocurrió un error interno al pensar la respuesta."}), 500

# --- RUTA DE PRUEBA ANTIGUA (Se mantiene intacta) ---
@app.route('/test-nido')
def test_nido():
    datos_de_prueba = { "nombre_negocio": "Ferretería El Tornillo Feliz", "titulo_personalizado": "Diagnóstico y Oportunidades para Ferretería El Tornillo Feliz", "texto_diagnostico": "Hemos detectado que su sitio web actual no ofrece a los clientes una forma inmediata de contacto...", "ejemplo_pregunta_1": "¿Tienen stock de taladros inalámbricos DeWalt?", "ejemplo_respuesta_1": "¡Claro que sí! Tenemos el modelo DCD777C2 a $120.00...", "ejemplo_pregunta_2": "¿Hasta qué hora están abiertos hoy?", "ejemplo_respuesta_2": "Hoy estamos abiertos hasta las 6:00 PM...", "texto_contenido_de_valor": "Un Agente de IA no solo responde preguntas..." }
    return render_template('nido_template.html', **datos_de_prueba)

# --- NUEVO FLUJO DEL "PRE-NIDO" (Se mantiene intacto) ---
@app.route('/pre-nido/<uuid:id_unico>')
def mostrar_pre_nido(id_unico):
    # (Tu código original para esta ruta va aquí, sin cambios)
    pass

# --- RUTA GENERAR-NIDO (Se mantiene intacta) ---
@app.route('/generar-nido', methods=['POST'])
def generar_nido_y_enviar_enlace():
    # (Tu código original para esta ruta va aquí, sin cambios)
    pass

# --- BLOQUE DE ARRANQUE DEL SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
