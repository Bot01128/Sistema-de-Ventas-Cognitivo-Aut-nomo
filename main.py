import os
import psycopg2
import json
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from flask_babel import Babel
from cerebro_dashboard import create_dashboard_brain

# --- CONFIGURACIÓN INICIAL ---
app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Configurar la IA de Google globalmente
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print(">>> IA de Google configurada exitosamente para la aplicación.")

def get_locale():
    # Detecta el idioma del navegador del usuario. Si no lo encuentra, usa 'es' por defecto.
    if not request.accept_languages:
        return 'es'
    return request.accept_languages.best_match(['en', 'es'])

babel = Babel(app, locale_selector=get_locale)
app.jinja_env.globals.update(get_locale=get_locale)

# --- CEREBRO DEL DASHBOARD EXISTENTE (Funcionalidad que no se toca) ---
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

# --- RUTA DE PRUEBA ANTIGUA (Se mantiene por seguridad) ---
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

# --- NUEVO FLUJO DEL "PRE-NIDO" V3.2 (CON IA MULTILINGÜE) ---

@app.route('/pre-nido/<uuid:id_unico>')
def mostrar_pre_nido(id_unico):
    """Muestra la página de 'aporte de valor' en el idioma del usuario, generada por IA."""
    
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

        # --- ¡LA MAGIA DE LA IA MULTILINGÜE! ---
        if not GOOGLE_API_KEY:
            return "Error: La clave de API de Google no está configurada.", 500

        prompt = f"""
        Actúa como un experto en marketing y un traductor profesional. Tu misión es generar un objeto JSON con los textos para una página web de marketing, traducidos al idioma con el código '{idioma_detectado}'.

        El nombre del negocio del prospecto es: "{nombre_negocio}"

        TAREA: Genera un objeto JSON con las siguientes claves, con su contenido traducido perfectamente al idioma '{idioma_detectado}':
        1. "titulo_valor": "3 Formas de Aumentar Ventas para {nombre_negocio}"
        2. "texto_valor": "El marketing de contenidos es clave. Un blog relevante atrae clientes. La automatización de respuestas en redes sociales captura leads 24/7. Nosotros nos especializamos en esto último."
        3. "h2_siguiente_nivel": "¿Listo para el Siguiente Nivel?"
        4. "p1_diagnostico": "Lo anterior es solo una idea general. Hemos preparado un <strong>diagnóstico interactivo y 100% personalizado</strong> para <strong>{nombre_negocio}</strong>, donde verás ejemplos reales de cómo un Agente de IA podría transformar tu comunicación con los clientes."
        5. "p2_gratis": "Es gratuito y sin compromiso. Simplemente introduce tu correo para generar tu acceso al instante."
        6. "placeholder_email": "Tu mejor correo para recibir el acceso"
        7. "texto_boton": "Generar mi Diagnóstico Personalizado"

        IMPORTANTE: El nombre del negocio '{nombre_negocio}' no debe ser traducido. Devuelve solo el objeto JSON, sin explicaciones ni nada más.
        """
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        # Limpiar la respuesta para que sea un JSON válido
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        textos = json.loads(json_text)
        
        print(f">>> Contenido multilingüe generado por IA para el idioma '{idioma_detectado}'.")

        return render_template('pre_nido.html', 
                               prospecto_id=prospecto_id, 
                               nombre_negocio=nombre_negocio,
                               textos=textos
                               )
    except Exception as e:
        print(f"!!! ERROR al mostrar pre-nido con IA multilingüe: {e} !!!")
        return "Error al cargar la página.", 500
    finally:
        if conn:
            cur.close()
            conn.close()

@app.route('/generar-nido', methods=['POST'])
def generar_nido_y_enviar_enlace():
    # ... (Tu código funcional de generar-nido se mantiene aquí, omitido por brevedad) ...
    email_cliente = request.form.get('email_prospecto')
    prospecto_id = request.form.get('prospecto_id_oculto')
    
    print(f"EMAIL CAPTURADO: {email_cliente} para el prospecto ID: {prospecto_id}. Redirigiendo al Nido...")
    
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
        print(f"Error recuperando nombre para el nido: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
            
    # TAREA PENDIENTE: Llamar a la IA para generar el contenido del Nido.
    datos_del_nido = {
        "nombre_negocio": nombre_negocio,
        "titulo_personalizado": f"Diagnóstico y Oportunidades para {nombre_negocio}",
        "texto_diagnostico": "Hemos detectado que su sitio web actual no ofrece a los clientes una forma inmediata de contacto, como un chat en vivo, lo que podría estar causando la pérdida de clientes impacientes.",
        "ejemplo_pregunta_1": "¿Tienen stock de taladros inalámbricos DeWalt?",
        "ejemplo_respuesta_1": "¡Claro que sí! Tenemos el modelo DCD777C2 a $120.00. Incluye 2 baterías y cargador. ¿Le gustaría que le reservemos uno?",
        "ejemplo_pregunta_2": "¿Hasta qué hora están abiertos hoy?",
        "ejemplo_respuesta_2": "Hoy estamos abiertos hasta las 6:00 PM. ¡Lo esperamos!",
        "texto_contenido_de_valor": "Un Agente de IA no solo responde preguntas, también puede capturar los datos de contacto de clientes potenciales fuera de horario, asegurando que ninguna oportunidad de venta se pierda."
    }
    
    return render_template('nido_template.html', **datos_del_nido)

# --- BLOQUE DE ARRANQUE DEL SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
