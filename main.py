import os
import psycopg2
import json
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from flask_babel import Babel, gettext
from cerebro_dashboard import create_chatbot

# --- NO TOCAMOS LAS IMPORTACIONES DE LOS TRABAJADORES POR AHORA ---
# from trabajador_orquestador import orquestar_nueva_caza
# from trabajador_cazador import cazar_prospectos

# =====================================================================
# SECCIÓN 1: INICIALIZACIÓN DE LA APLICACIÓN Y BABEL
# =====================================================================
app = Flask(__name__)

# Definimos la función para obtener el idioma del navegador del usuario.
def get_locale():
    # Encuentra el mejor idioma entre 'en' (inglés) y 'es' (español).
    return request.accept_languages.best_match(['en', 'es'])

# Conectamos Babel a nuestra aplicación Flask.
babel = Babel(app, locale_selector=get_locale)


# =====================================================================
# SECCIÓN 2: PROCESADOR DE CONTEXTO (LA SOLUCIÓN CLAVE)
# =====================================================================
# Este bloque es la forma correcta y segura de hacer que las funciones
# de traducción estén disponibles en TODOS los archivos HTML (plantillas).
@app.context_processor
def inject_global_funcs():
    # Devuelve un diccionario con las funciones que queremos disponibles.
    # Ahora, cualquier plantilla puede usar {{ _('texto') }} y {{ get_locale() }}.
    return dict(get_locale=get_locale, _=gettext)


# =====================================================================
# SECCIÓN 3: CONFIGURACIÓN DE SERVICIOS EXTERNOS
# =====================================================================
DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print(">>> DIAGNÓSTICO: API de Google configurada.")

# =====================================================================
# SECCIÓN 4: LÓGICA DE NEGOCIO (INICIALIZACIÓN DEL CEREBRO)
# =====================================================================
ID_DE_LA_CAMPAÑA_ACTUAL = 1 
descripcion_de_la_campana = "Soy un asistente virtual genérico."

try:
    print(">>> DIAGNÓSTICO: Intentando conectar a la base de datos para obtener descripción...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT descripcion_producto FROM campanas WHERE id = %s", (ID_DE_LA_CAMPAÑA_ACTUAL,))
    result = cur.fetchone()
    if result and result[0]:
        descripcion_de_la_campana = result[0]
        print(">>> DIAGNÓSTICO: Descripción obtenida de la base de datos.")
    else:
        print(">>> DIAGNÓSTICO: No se encontró descripción para la campaña, usando valor por defecto.")
    cur.close()
    conn.close()
except Exception as e:
    print(f"!!! ADVERTENCIA: No se pudo conectar a la DB para obtener la descripción. Error: {e}")
    pass

# Inicializamos el cerebro del chat con la descripción obtenida.
dashboard_brain = create_chatbot(descripcion_producto=descripcion_de_la_campana)
print(">>> DIAGNÓSTICO: Cerebro del dashboard inicializado.")


# =====================================================================
# SECCIÓN 5: RUTAS DE LA APLICACIÓN (LAS PÁGINAS)
# =====================================================================

# Ruta raíz, redirige al dashboard.
@app.route('/')
def index():
    return render_template('dashboard.html')

# Ruta para el dashboard principal.
@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

# Ruta para nido_template.html
@app.route('/nido')
def nido_page():
    return render_template('nido_template.html')

# Ruta para pre_nido.html
@app.route('/pre-nido')
def pre_nido_page():
    return render_template('pre_nido.html')

# Ruta para la API del chat.
@app.route('/chat', methods=['POST'])
def chat():
    if not dashboard_brain:
        return jsonify({"error": "Chat no disponible."}), 500
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No hay mensaje."}), 400
    try:
        response_text = dashboard_brain.invoke({"question": user_message})
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": f"Ocurrió un error en el cerebro: {e}"}), 500

# Ruta para la API de lanzar campañas.
@app.route('/lanzar-campana', methods=['POST'])
def lanzar_campana():
    print("\n>>> RUTA /lanzar-campana: Orden recibida.")
    orden_del_cliente = request.get_json()
    if not orden_del_cliente:
        return jsonify({"error": "No se recibieron datos de la campaña."}), 400

    conn = None
    try:
        print(">>> RUTA /lanzar-campana: Guardando orden en la cola de trabajos...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        sql_insert = "INSERT INTO cola_de_trabajos (tipo_trabajo, datos_json) VALUES (%s, %s);"
        datos_como_texto_json = json.dumps(orden_del_cliente)
        cur.execute(sql_insert, ('cazar_prospectos', datos_como_texto_json))
        conn.commit()
        print(">>> RUTA /lanzar-campana: Orden guardada con éxito.")
        return jsonify({"message": "¡Campaña recibida! Hemos empezado a trabajar en ello."})
    except Exception as e:
        print(f"!!! ERROR FATAL en /lanzar-campana: {e}")
        return jsonify({"error": f"Ocurrió un error en el servidor: {e}"}), 500
    finally:
        if conn:
            conn.close()

# =====================================================================
# SECCIÓN 6: BLOQUE DE ARRANQUE DE LA APLICACIÓN
# =====================================================================
if __name__ == '__main__':
    # Usamos el puerto que Fly.io nos asigna, o el 8080 por defecto.
    port = int(os.environ.get('PORT', 8080))
    # 'host' debe ser '0.0.0.0' para que sea accesible desde fuera del contenedor.
    app.run(host='0.0.0.0', port=port)
