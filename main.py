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

# --- CÁMARA DE DIAGNÓSTICO (LA DEJAMOS POR AHORA) ---
print("=====================================================")
print(">>> [DIAGNÓSTICO] INICIANDO APLICACIÓN...")
if DATABASE_URL:
    print(">>> [DIAGNÓSTICO] DATABASE_URL encontrada. Comienza con:", DATABASE_URL[:30]) 
else:
    print("!!! ERROR [DIAGNÓSTICO]: ¡DATABASE_URL NO FUE ENCONTRADA!")
print("=====================================================")

# Configurar la IA de Google globalmente
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print(">>> [main.py] IA de Google configurada.!!!")
else:
    print("!!! WARNING [main.py]: GOOGLE_API_KEY no encontrada.")

# --- LÓGICA PARA CARGAR LA PERSONALIDAD DE LA CAMPAÑA ---
ID_DE_LA_CAMPAÑA_ACTUAL = 1 
descripcion_de_la_campana = "Soy un asistente virtual genérico."
try:
    print(f">>> [main.py] Buscando descripción para la campaña ID: {ID_DE_LA_CAMPAÑA_ACTUAL}...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT descripcion_producto FROM campanas WHERE id = %s", (ID_DE_LA_CAMPAÑA_ACTUAL,))
    result = cur.fetchone()
    if result and result[0]:
        descripcion_de_la_campana = result[0]
        print(">>> [DIAGNÓSTICO] ¡ÉXITO! Se encontró la descripción en Supabase.")
    else:
        print("!!! ERROR [DIAGNÓSTICO]: No se encontró la campaña con ID 1.")
    cur.close()
    conn.close()
except Exception as e:
    print(f"!!! ERROR FATAL [DIAGNÓSTICO]: ¡LA CONEXIÓN A SUPABASE FALLÓ! Error: {e}")

# --- INICIALIZACIÓN DEL CEREBRO ---
dashboard_brain = create_chatbot(descripcion_producto=descripcion_de_la_campana)
if dashboard_brain:
    print(">>> [main.py] Cerebro con personalidad inicializado.")
else:
    print("!!! ERROR [main.py]: El cerebro no pudo ser inicializado.")

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
    # ... (esta función se queda exactamente igual) ...
    if not dashboard_brain:
        print("!!! ERROR [/chat]: Intento de chat con cerebro no inicializado.")
        return jsonify({"error": "El servicio de chat no está disponible."}), 500
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No hay mensaje."}), 400
    try:
        response_text = dashboard_brain.invoke({"question": user_message})
        return jsonify({"response": response_text})
    except Exception as e:
        print(f"!!! ERROR fatal en la ruta /chat: {e} !!!")
        return jsonify({"error": "Ocurrió un error inesperado."}), 500

# --- RUTAS RESTAURADAS DEL PROYECTO NIDO ---

@app.route('/pre-nido/<uuid:id_unico>')
def mostrar_pre_nido(id_unico):
    # SIMULACIÓN DE DATOS (en el futuro, esto vendrá de la base de datos)
    nombre_del_negocio_prospecto = "Ferretería El Tornillo Feliz"
    textos_para_la_pagina = {
        "titulo_valor": f"Una Oportunidad Única para {nombre_del_negocio_prospecto}",
        "texto_valor": "Hemos identificado áreas clave donde la automatización con IA puede potenciar tu comunicación, ahorrarte tiempo y aumentar tus ventas.",
        "h2_siguiente_nivel": "Lleva tu Negocio al Siguiente Nivel",
        "p1_diagnostico": "Basado en nuestro análisis inicial, hemos preparado un <strong>diagnóstico personalizado</strong> que revela cómo un Agente de IA puede transformar tu interacción con los clientes.",
        "p2_gratis": "Este diagnóstico es completamente gratis y sin compromiso. Solo necesitamos tu correo electrónico para enviártelo.",
        "placeholder_email": "Escribe tu mejor correo electrónico aquí",
        "texto_boton": "¡Quiero mi Diagnóstico Gratis!"
    }
    return render_template('pre_nido.html', 
                           prospecto_id=str(id_unico), 
                           nombre_negocio=nombre_del_negocio_prospecto,
                           textos=textos_para_la_pagina)

@app.route('/generar-nido', methods=['POST'])
def generar_nido_y_enviar_enlace():
    # SIMULACIÓN DE DATOS (en el futuro, esto vendrá de la IA)
    datos_para_el_nido = {
        "nombre_negocio": "Ferretería El Tornillo Feliz",
        "titulo_personalizado": "Tu Nuevo Vendedor Estrella Trabaja 24/7",
        "texto_diagnostico": "Hemos notado que tus clientes preguntan frecuentemente por horarios y disponibilidad de productos fuera de tu horario de atención. Un Agente de IA puede capturar esas ventas perdidas.",
        "ejemplo_pregunta_1": "¿Tienen tornillos de anclaje de acero galvanizado?",
        "ejemplo_respuesta_1": "¡Claro que sí! Nuestros tornillos de anclaje son ideales para la industria pesada. ¿Para qué tipo de proyecto los necesitas?",
        "ejemplo_pregunta_2": "¿Y hasta qué hora trabajan los sábados?",
        "ejemplo_respuesta_2": "Los sábados estamos abiertos de 8am a 6pm. ¡Te esperamos!",
        "texto_contenido_de_valor": "Además de responder preguntas, un Agente IA puede sugerir productos complementarios, aumentando el valor de cada venta."
    }
    return render_template('nido_template.html', **datos_para_el_nido)


# --- BLOQUE DE ARRANQUE ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
