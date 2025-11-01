import os
import psycopg2
import json
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from flask_babel import Babel
from cerebro_dashboard import create_dashboard_brain
from supabase import create_client, Client
from dotenv import load_dotenv

# --- CONFIGURACIÓN INICIAL ---
load_dotenv() # Cargar variables de entorno desde el archivo .env

app = Flask(__name__)

# --- Conexión a Base de Datos (Prioridad Supabase, fallback a DATABASE_URL) ---
DATABASE_URL = os.environ.get("DATABASE_URL")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(">>> Conexión a Supabase establecida exitosamente.")
    except Exception as e:
        print(f"!!! ERROR al inicializar Supabase: {e} !!!")
else:
    print("--- ADVERTENCIA: No se encontraron las credenciales de Supabase. Se usará DATABASE_URL si está disponible. ---")

# --- Configuración de la IA de Google ---
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print(">>> IA de Google configurada exitosamente para la aplicación.")

# --- Configuración de Idioma (Babel) ---
def get_locale():
    if not request.accept_languages:
        return 'es'
    return request.accept_languages.best_match(['en', 'es'])

babel = Babel(app, locale_selector=get_locale)
app.jinja_env.globals.update(get_locale=get_locale)

# --- CEREBRO DEL DASHBOARD (Funcionalidad que no se toca) ---
dashboard_brain = create_dashboard_brain()

# --- RUTAS DE LA APLICACIÓN ---

# --- Ruta Principal (Tu Dashboard) ---
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# --- Ruta de Chat para el Dashboard ---
@app.route('/chat', methods=['POST'])
def chat():
    # ... (Tu código de chat existente se mantiene intacto) ...
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

# --- NUEVA RUTA PARA CREAR CAMPAÑAS (Integrada) ---
@app.route('/crear-campana', methods=['POST'])
def crear_campana():
    if not supabase:
        return jsonify({"status": "error", "message": "La conexión con la base de datos (Supabase) no está configurada."}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No se recibieron datos en la petición."}), 400

        # Extraer y validar datos del formulario
        required_fields = ['tipo_negocio', 'ciudad', 'pais', 'cantidad_prospectos', 'idioma']
        if not all(field in data for field in required_fields):
            return jsonify({"status": "error", "message": "Faltan campos requeridos en la petición."}), 400

        campaign_data = {
            'tipo_negocio': data.get('tipo_negocio'),
            'ciudad': data.get('ciudad'),
            'pais': data.get('pais'),
            'cantidad_prospectos': data.get('cantidad_prospectos'),
            'idioma': data.get('idioma'),
            'estado': 'activa'
        }

        # Insertar en la tabla 'Campanas'
        api_response = supabase.table('Campanas').insert(campaign_data).execute()

        if api_response.data:
            return jsonify({"status": "success", "message": "Campaña creada exitosamente", "data": api_response.data}), 201
        else:
            # Captura errores que no lanzan una excepción directa en la librería
            error_message = api_response.get('error', {}).get('message', 'Error desconocido al guardar la campaña.')
            return jsonify({"status": "error", "message": error_message}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error interno del servidor: {str(e)}"}), 500

# --- RUTAS PARA VISUALIZAR LOS OTROS HTMLs (Añadidas) ---

@app.route('/nido-template')
def ver_nido_template():
    """Ruta para previsualizar el nido_template.html con datos de ejemplo."""
    datos_de_prueba = {
        "nombre_negocio": "Ejemplo de Negocio",
        "titulo_personalizado": "Diagnóstico para Ejemplo de Negocio",
        "texto_diagnostico": "Este es un texto de diagnóstico de ejemplo para la plantilla del nido.",
        "ejemplo_pregunta_1": "¿Pregunta de ejemplo 1?",
        "ejemplo_respuesta_1": "Respuesta de ejemplo 1.",
        "ejemplo_pregunta_2": "¿Pregunta de ejemplo 2?",
        "ejemplo_respuesta_2": "Respuesta de ejemplo 2.",
        "texto_contenido_de_valor": "Este es un contenido de valor de ejemplo."
    }
    return render_template('nido_template.html', **datos_de_prueba)

@app.route('/pre-nido-template')
def ver_pre_nido_template():
    """Ruta para previsualizar el pre_nido.html con datos de ejemplo."""
    textos_de_prueba = {
        "titulo_valor": "Título de Aporte de Valor de Ejemplo",
        "texto_valor": "Texto de aporte de valor de ejemplo.",
        "h2_siguiente_nivel": "¿Listo para el Siguiente Nivel?",
        "p1_diagnostico": "Hemos preparado un <strong>diagnóstico de ejemplo</strong> para <strong>tu negocio</strong>.",
        "p2_gratis": "Es gratuito y sin compromiso.",
        "placeholder_email": "Tu correo de ejemplo",
        "texto_boton": "Generar Diagnóstico de Ejemplo"
    }
    return render_template('pre_nido.html', prospecto_id=0, nombre_negocio="Negocio de Ejemplo", textos=textos_de_prueba)


# --- CÓDIGO ANTIGUO (Se mantiene sin cambios por ahora) ---
# Todas tus rutas existentes como /pre-nido/<uuid:id_unico> y /generar-nido se mantienen aquí.
# Las he omitido en este bloque para no repetir, pero debes asegurarte de que estén en tu archivo final.

@app.route('/pre-nido/<uuid:id_unico>')
def mostrar_pre_nido(id_unico):
    # ... (Tu código funcional se mantiene aquí) ...
    pass # Reemplaza este 'pass' con tu código original de esta función

@app.route('/generar-nido', methods=['POST'])
def generar_nido_y_enviar_enlace():
    # ... (Tu código funcional se mantiene aquí) ...
    pass # Reemplaza este 'pass' con tu código original de esta función


# --- BLOQUE DE ARRANQUE DEL SERVIDOR ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
