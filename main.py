import os
import psycopg2
from flask import Flask, render_template, request, jsonify
from flask_babel import Babel
from cerebro_dashboard import create_dashboard_brain

# --- CONFIGURACIÓN INICIAL ---
app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_locale():
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
    # ... (Tu código de chat funcional se mantiene aquí, omitido por brevedad) ...
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
    # ... (Tu código de test-nido se mantiene aquí, omitido por brevedad) ...
    datos_de_prueba = {
        "nombre_negocio": "Ferretería El Tornillo Feliz",
        "titulo_personalizado": "Diagnóstico y Oportunidades para Ferretería El Tornillo Feliz",
        "texto_diagnostico": "Hemos detectado que su sitio web actual no ofrece a los clientes una forma inmediata de contacto, como un chat en vivo...",
        "ejemplo_pregunta_1": "¿Tienen stock de taladros inalámbricos DeWalt?",
        "ejemplo_respuesta_1": "¡Claro que sí! Tenemos el modelo DCD777C2 a $120.00...",
        "ejemplo_pregunta_2": "¿Hasta qué hora están abiertos hoy?",
        "ejemplo_respuesta_2": "Hoy estamos abiertos hasta las 6:00 PM. ¡Lo esperamos!",
        "texto_contenido_de_valor": "Un Agente de IA no solo responde preguntas, también puede capturar los datos de contacto de clientes potenciales..."
    }
    return render_template('nido_template.html', **datos_de_prueba)


# --- NUEVO FLUJO DEL "PRE-NIDO" V3.0 ---

@app.route('/pre-nido/<uuid:id_unico>')
def mostrar_pre_nido(id_unico):
    """Muestra la página de 'aporte de valor' antes de pedir el email."""
    print(f"--- Solicitud de Pre-Nido para ID: {id_unico} ---")
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        # Buscamos el ID y el nombre del prospecto usando el id_unico
        cur.execute("SELECT id, nombre_negocio FROM prospectos WHERE id_unico = %s", (str(id_unico),))
        prospecto = cur.fetchone()

        if not prospecto:
            return "Enlace no válido.", 404
        
        prospecto_id, nombre_negocio = prospecto

        # TAREA PENDIENTE: Llamar a la IA para generar contenido de valor único aquí
        # Por ahora, usamos texto de ejemplo
        titulo_valor = f"3 Formas de Aumentar Ventas para {nombre_negocio}"
        texto_valor = "El marketing de contenidos es clave. Un blog relevante atrae clientes. La automatización de respuestas en redes sociales captura leads 24/7. Y ofrecer demos personalizadas cierra ventas. Nosotros nos especializamos en las dos últimas."

        return render_template('pre_nido.html', 
                               prospecto_id=prospecto_id, 
                               nombre_negocio=nombre_negocio,
                               titulo_contenido_de_valor=titulo_valor,
                               texto_contenido_de_valor=texto_valor)
    except Exception as e:
        print(f"!!! ERROR al mostrar pre-nido: {e} !!!")
        return "Error al cargar la página.", 500
    finally:
        if conn:
            cur.close()
            conn.close()

@app.route('/generar-nido', methods=['POST'])
def generar_nido_y_enviar_enlace():
    """Recibe el email y redirige al Nido final (en el futuro, enviará un enlace)."""
    email_cliente = request.form.get('email_prospecto')
    prospecto_id = request.form.get('prospecto_id_oculto')
    
    # --- TAREA PENDIENTE ---
    # 1. Guardar el `email_cliente` en la base de datos para el `prospecto_id`.
    # 2. Activar al "Nutridor" para este prospecto.
    # 3. En lugar de redirigir, en el futuro generaremos un token y enviaremos un email.
    # ------------------------
    
    print(f"EMAIL CAPTURADO: {email_cliente} para el prospecto ID: {prospecto_id}. Redirigiendo al Nido...")
    
    # Por ahora, simplemente redirigimos al Nido final usando el prospecto_id
    # En el futuro, será a una URL con un token único.
    # Esta es una implementación temporal para probar el flujo.
    # Aquí iría la lógica para mostrar el `nido_template.html` dinámico.
    # Vamos a reutilizar la lógica de `test_nido` por ahora.
    
    # Obtenemos el nombre del negocio para la redirección
    nombre_negocio = "tu negocio" # Valor temporal
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

    # TAREA PENDIENTE: Aquí deberíamos llamar a la IA para generar el contenido del Nido.
    # Por ahora, usamos los datos de prueba para demostrar el flujo.
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
    app.run(host='='0.0.0.0', port=port)
