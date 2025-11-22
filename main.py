import os
import psycopg2
import json
import google.generativeai as genai
import uuid
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_babel import Babel
from psycopg2.extras import Json
from werkzeug.routing import BaseConverter
from cerebro_dashboard import create_chatbot

# --- CONFIGURACION INICIAL ---
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "una-clave-secreta-muy-robusta-para-desarrollo")

# Convertidor de UUID para las URLs
class UUIDConverter(BaseConverter):
    def to_python(self, value): return uuid.UUID(value)
    def to_url(self, value): return str(value)

app.url_map.converters['uuid'] = UUIDConverter

# --- BLOQUE DE CONFIGURACION DE IDIOMAS ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(basedir, 'translations')

def get_locale():
    if not request.accept_languages: return 'es'
    return request.accept_languages.best_match(['en', 'es'])

babel = Babel(app, locale_selector=get_locale)

@app.context_processor
def inject_get_locale():
    return dict(get_locale=get_locale)

# --- INICIALIZACION DE BASE DE DATOS Y API KEYS ---
DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# --- LAZY LOADING DEL CEREBRO DE LA IA (DASHBOARD) ---
dashboard_brain = None
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# --- HELPER DE BASE DE DATOS ---
def get_db_connection():
    """Crea una conexión segura a la base de datos."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"!!! ERROR CONECTANDO A DB: {e}")
        return None

# --- FUNCION AUXILIAR DE IA PARA EL NIDO ---
def generar_contenido_nido_con_ia(negocio, dolores, producto):
    """Genera el contenido del Showroom dinámicamente usando Gemini."""
    try:
        if not GOOGLE_API_KEY: raise Exception("Sin API Key")
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Genera un JSON con contenido para una landing page de ventas (Showroom) para el negocio '{negocio}'.
        
        CONTEXTO:
        Dolores detectados: {dolores}
        Nuestro Producto: {producto}
        
        FORMATO JSON REQUERIDO (Solo devuelve el JSON):
        {{
            "titulo": "Un título impactante y personalizado",
            "diagnostico": "Un párrafo de 3 líneas diagnosticando sus problemas sutilmente.",
            "chat_q1": "Una pregunta que un cliente típico de {negocio} haría.",
            "chat_a1": "Una respuesta ideal dada por una IA.",
            "chat_q2": "Otra pregunta difícil de un cliente.",
            "chat_a2": "Otra respuesta perfecta de la IA.",
            "valor": "Un consejo breve de alto valor sobre cómo mejorar su negocio hoy mismo."
        }}
        """
        response = model.generate_content(prompt)
        # Limpieza básica del JSON string para evitar errores de parseo
        texto_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(texto_json)
    except Exception as e:
        print(f"Error IA Nido: {e}. Usando contenido por defecto.")
        # Fallback por si la IA falla
        return {
            "titulo": f"Estrategia de Crecimiento para {negocio}",
            "diagnostico": "Hemos detectado oportunidades clave para optimizar la atención al cliente y automatizar respuestas frecuentes.",
            "chat_q1": "¿Tienen disponibilidad para hoy?",
            "chat_a1": "¡Hola! Sí, tenemos agenda disponible. ¿Deseas reservar ahora?",
            "chat_q2": "¿Cuáles son sus precios?",
            "chat_a2": "Nuestros precios varían según el servicio. ¿Te gustaría ver nuestro catálogo?",
            "valor": "La automatización puede recuperar hasta un 30% de las ventas perdidas por falta de respuesta inmediata."
        }

# --- RUTA DE HEALTHCHECK PARA RAILWAY ---
@app.route('/health')
def health_check():
    return "OK", 200

# --- RUTAS PRINCIPALES DE LA APLICACION ---
@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/cliente')
def client_dashboard():
    return render_template('client_dashboard.html')

@app.route('/mis-clientes')
def mis_clientes():
    return render_template('mis_clientes.html')

@app.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/taller')
def admin_taller():
    return render_template('admin_taller.html')

# --- CHATBOT DEL DASHBOARD (Legacy Support) ---
@app.route('/chat', methods=['POST'])
def chat():
    global dashboard_brain
    try:
        if dashboard_brain is None:
            print(">>> [main.py - LAZY LOADING] Primer mensaje de chat recibido. INICIALIZANDO CEREBRO...")
            # Nota: Aquí mantenemos la compatibilidad con tu tabla antigua 'campanas' si existe,
            # o usamos un string por defecto para no romper nada.
            descripcion_de_la_campana = "Soy un asistente virtual de AutoNeura."
            
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                try:
                    # Intentamos leer de la tabla antigua si existe para el dashboard admin
                    cur.execute("SELECT descripcion_producto FROM campanas WHERE id = 1")
                    result = cur.fetchone()
                    if result and result[0]:
                        descripcion_de_la_campana = result[0]
                except Exception:
                    print("Aviso: Tabla 'campanas' no encontrada o vacía, usando descripción por defecto.")
                    conn.rollback()
                finally:
                    cur.close()
                    conn.close()
            
            dashboard_brain = create_chatbot(descripcion_producto=descripcion_de_la_campana)
            print(">>> [main.py - LAZY LOADING] Cerebro inicializado y listo para reusar.")
        
        user_message = request.json.get('message')
        if not user_message: return jsonify({"error": "No hay mensaje."}), 400
        
        response_text = dashboard_brain.invoke({"question": user_message})
        return jsonify({"response": response_text})

    except Exception as e:
        print(f"!!! ERROR FATAL en la ruta /chat: {e}")
        return jsonify({"error": f"Ocurrio un error en el chat: {e}"}), 500

# --- RUTAS DEL SISTEMA DE PERSUASIÓN (NUEVO FLUJO) ---

@app.route('/pre-nido/<uuid:id_unico>')
def mostrar_pre_nido(id_unico):
    """
    Paso 1: El prospecto llega desde el email del Persuasor.
    Validamos el token y mostramos la página de captura.
    """
    conn = get_db_connection()
    if not conn: return "Error de conexión", 500
    
    cur = conn.cursor()
    try:
        # Buscamos en la tabla 'prospects' usando el token único
        cur.execute("SELECT id, business_name FROM prospects WHERE unique_access_token = %s", (str(id_unico),))
        resultado = cur.fetchone()
        
        if resultado:
            prospecto_id, nombre_negocio = resultado
            return render_template('persuasor.html', prospecto_id=prospecto_id, nombre_negocio=nombre_negocio)
        else:
            return "Enlace inválido o expirado.", 404
    except Exception as e:
        print(f"Error en pre-nido: {e}")
        return "Error procesando la solicitud", 500
    finally:
        cur.close()
        conn.close()

@app.route('/generar-nido', methods=['POST'])
def generar_nido_y_enviar_enlace():
    """
    Paso 2: El prospecto deja su email.
    Actualizamos DB, generamos contenido IA y mostramos el Nido inmediatamente.
    """
    email = request.form.get('email')
    prospecto_id = request.form.get('prospecto_id')
    
    if not email or not prospecto_id:
        return "Faltan datos", 400

    conn = get_db_connection()
    if not conn: return "Error de conexión", 500

    try:
        cur = conn.cursor()
        
        # 1. Actualizar prospecto (Captura de Lead)
        cur.execute("""
            UPDATE prospects 
            SET captured_email = %s, 
                status = 'nutriendo',
                last_interaction_at = NOW()
            WHERE id = %s
            RETURNING business_name, pain_points, campaign_id
        """, (email, prospecto_id))
        
        datos_prospecto = cur.fetchone()
        conn.commit() # Guardamos el email pase lo que pase después
        
        if not datos_prospecto:
            return "Error identificando prospecto", 404
            
        nombre_negocio, pain_points, campaign_id = datos_prospecto
        
        # 2. Obtener datos de la campaña para contexto de la IA
        desc_producto = "Servicios de IA Avanzada"
        if campaign_id:
            cur.execute("SELECT product_description FROM campaigns WHERE id = %s", (campaign_id,))
            res_camp = cur.fetchone()
            if res_camp: desc_producto = res_camp[0]

        cur.close()
        conn.close()

        # 3. Generar contenido del Showroom (Nido) con IA
        contenido_nido = generar_contenido_nido_con_ia(nombre_negocio, pain_points, desc_producto)
        
        # 4. Renderizar el Nido
        return render_template('nido_template.html',
                               nombre_negocio=nombre_negocio,
                               titulo_personalizado=contenido_nido['titulo'],
                               texto_diagnostico=contenido_nido['diagnostico'],
                               ejemplo_pregunta_1=contenido_nido['chat_q1'],
                               ejemplo_respuesta_1=contenido_nido['chat_a1'],
                               ejemplo_pregunta_2=contenido_nido['chat_q2'],
                               ejemplo_respuesta_2=contenido_nido['chat_a2'],
                               texto_contenido_de_valor=contenido_nido['valor'],
                               prospecto_id=prospecto_id)

    except Exception as e:
        print(f"!!! ERROR en generar-nido: {e}")
        if conn: conn.close()
        return "Ocurrió un error inesperado.", 500

@app.route('/api/chat-nido', methods=['POST'])
def chat_nido_api():
    """API para el chat simulado dentro del Nido."""
    data = request.json
    mensaje = data.get('mensaje', '')
    # Aquí conectaremos el Nutridor en el futuro. Por ahora, respuesta empática.
    return jsonify({
        "respuesta": "Gracias por tu pregunta. Estoy analizando tu consulta para darte la mejor respuesta. Mientras tanto, revisa la sección de demostración arriba."
    })

# --- RUTAS DE APOYO Y PRUEBA ---
@app.route('/confirmacion')
def mostrar_confirmacion():
    return render_template('confirmacion.html')

@app.route('/ver-pre-nido')
def ver_pre_nido():
    # Ruta para testear el diseño sin token real
    return render_template('persuasor.html', prospecto_id="prueba", nombre_negocio="Negocio de Prueba")

@app.route('/ver-nido')
def ver_nido():
    # Ruta para testear el diseño del nido sin datos reales
    return render_template('nido_template.html', 
                           nombre_negocio="Negocio Demo",
                           titulo_personalizado="Tu Oportunidad de Crecimiento",
                           texto_diagnostico="Diagnóstico de prueba...",
                           texto_contenido_de_valor="Contenido de valor aquí...")

# --- BLOQUE DE ARRANQUE ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
