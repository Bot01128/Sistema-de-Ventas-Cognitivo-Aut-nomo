import os
import psycopg2
from flask import Flask, render_template, request, jsonify
from flask_babel import Babel
from cerebro_dashboard import create_dashboard_brain

# --- CONFIGURACIÓN INICIAL ---
app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_locale():
    # Asegurémonos de tener un valor predeterminado si accept_languages está vacío
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

# --- RUTA DE PRUEBA ANTIGUA (La mantenemos por si acaso) ---
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
    return render_template('nido_template.html', **datos_de_prueba)

# --- NUEVAS RUTAS PARA EL NIDO DE CONVERSIÓN v2.0 ---

@app.route('/diagnostico/<uuid:id_unico>')
def pagina_de_captura(id_unico):
    """Muestra la página para que el prospecto introduzca su email."""
    print(f"--- Solicitud de página de captura para ID: {id_unico} ---")
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT id, nombre_negocio FROM prospectos WHERE id_unico = %s", (str(id_unico),))
        prospecto = cur.fetchone()

        if not prospecto:
            return "Enlace de diagnóstico no válido.", 404
        
        prospecto_id, nombre_negocio = prospecto
        return render_template('captura.html', prospecto_id=prospecto_id, nombre_negocio=nombre_negocio)
    except Exception as e:
        print(f"!!! ERROR al mostrar página de captura: {e} !!!")
        return "Error al cargar la página.", 500
    finally:
        if conn:
            cur.close()
            conn.close()

@app.route('/enviar-enlace', methods=['POST'])
def enviar_enlace_acceso():
    """Recibe el email, y en el futuro, generará el token y lo enviará."""
    email_cliente = request.form.get('email_prospecto')
    prospecto_id = request.form.get('prospecto_id_oculto')
    
    # --- TAREA PENDIENTE (FASE 2) ---
    # Aquí irá la lógica para:
    # 1. Generar un token único.
    # 2. Guardar el token y el email en la base de datos.
    # 3. Usar SendGrid para enviar el email con el enlace /nido/<token>.
    # --------------------------------
    
    print(f"EMAIL RECIBIDO: {email_cliente} para el prospecto ID: {prospecto_id}. TAREA PENDIENTE: Enviar enlace de acceso.")
    
    # Por ahora, solo mostramos un mensaje de confirmación
    # En el futuro, necesitaremos recuperar el `nombre_negocio` para que el mensaje sea perfecto
    return render_template('captura.html', nombre_negocio="tu negocio", mensaje="¡Excelente! Hemos enviado el enlace de acceso a tu correo. Por favor, revisa tu bandeja de entrada (y la de spam).")

# --- BLOQUE DE ARRANQUE DEL SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
