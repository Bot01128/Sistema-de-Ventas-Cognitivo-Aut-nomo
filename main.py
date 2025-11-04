import os
import psycopg2
import json
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from flask_babel import Babel
# ¡LA IMPORTACIÓN CORRECTA AL NUEVO CEREBRO!
from bot_de_respuesta.cerebro import create_chatbot

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

# --- INICIALIZACIÓN DEL NUEVO CEREBRO (EL TRASPLANTADO) ---
dashboard_brain = create_chatbot()
print(">>> [main.py] Nuevo cerebro con memoria (trasplantado) inicializado.")

# --- CONFIGURACIÓN DE IDIOMA (Tu código original, intacto) ---
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

# --- ¡¡¡RUTA DE CHAT COMPLETA Y ADAPTADA PARA EL NUEVO CEREBRO!!! ---
@app.route('/chat', methods=['POST'])
def chat():
    if not dashboard_brain:
        return jsonify({"error": "Cerebro no disponible. La inicialización falló."}), 500
    
    data = request.get_json()
    user_message = data.get('message')
    # Usaremos una session_id fija para probar, luego la haremos dinámica
    session_id = "dashboard_user_main" 
    
    if not user_message:
        return jsonify({"error": "No hay mensaje en la petición."}), 400
        
    try:
        print(f"--- [main.py] Invocando cerebro con: '{user_message}' para session_id: {session_id} ---")
        
        # Usamos la estructura que espera el nuevo cerebro con memoria
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

# --- RUTA DE PRUEBA ANTIGUA (Tu código original, intacto) ---
@app.route('/test-nido')
def test_nido():
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
    return render_template('nido_template.html', **datos_de_prueba)

# --- NUEVO FLUJO DEL "PRE-NIDO" (Tu código original, intacto) ---
@app.route('/pre-nido/<uuid:id_unico>')
def mostrar_pre_nido(id_unico):
    idioma_detectado = get_locale()
    print(f"--- Solicitud de Pre-Nido para ID: {id_unico} en idioma '{idioma_detectado}' ---")
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT id, nombre_negocio FROM prospectos WHERE id_unico = %s", (str(id_unico),))
        prospecto = cur.fetchone()
        if not prospecto:
            return "Enlace no válido.", 404
        prospecto_id, nombre_negocio = prospecto
        if not GOOGLE_API_KEY:
            return "Error: La clave de API de Google no está configurada.", 500
        prompt = f"""
        Actúa como un experto en marketing y un traductor profesional...
        """
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        textos = json.loads(json_text)
        print(f">>> Contenido multilingüe generado para '{idioma_detectado}'.")
        return render_template('pre_nido.html', prospecto_id=prospecto_id, nombre_negocio=nombre_negocio, textos=textos)
    except Exception as e:
        print(f"!!! ERROR al mostrar pre-nido: {e} !!!")
        return "Error al cargar la página.", 500
    finally:
        if conn:
            cur.close()
            conn.close()

# --- RUTA GENERAR-NIDO (Tu código original, intacto) ---
@app.route('/generar-nido', methods=['POST'])
def generar_nido_y_enviar_enlace():
    email_cliente = request.form.get('email_prospecto')
    prospecto_id = request.form.get('prospecto_id_oculto')
    print(f"EMAIL CAPTURADO: {email_cliente} para ID: {prospecto_id}. Redirigiendo...")
    nombre_negocio = "tu negocio"
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT nombre_negocio FROM prospectos WHERE id = %s", (prospecto_id,))
        resultado = cur.fetchone()
        if resultado:
            nombre_negocio = resultado[0]
    except Exception as e:
        print(f"Error recuperando nombre para nido: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
    datos_del_nido = {
        "nombre_negocio": nombre_negocio,
        "titulo_personalizado": f"Diagnóstico para {nombre_negocio}",
        "texto_diagnostico": "Hemos detectado una oportunidad de mejora...",
        "ejemplo_pregunta_1": "Pregunta de ejemplo 1",
        "ejemplo_respuesta_1": "Respuesta de ejemplo 1",
        "ejemplo_pregunta_2": "Pregunta de ejemplo 2",
        "ejemplo_respuesta_2": "Respuesta de ejemplo 2",
        "texto_contenido_de_valor": "Contenido de valor de ejemplo."
    }
    return render_template('nido_template.html', **datos_del_nido)

# --- BLOQUE DE ARRANQUE DEL SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
