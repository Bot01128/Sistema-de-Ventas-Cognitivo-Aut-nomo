import os
import psycopg2
import json
import google.generativeai as genai
import uuid
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_babel import Babel
from psycopg2.extras import Json
from werkzeug.routing import BaseConverter
from dotenv import load_dotenv

# --- IMPORTACIÓN DE MÓDULOS PROPIOS ---
# Importamos el chatbot del dashboard administrativo
try:
    from cerebro_dashboard import create_chatbot
except ImportError:
    print("!!! ADVERTENCIA: No se encontró cerebro_dashboard.py. El chat administrativo no funcionará.")
    create_chatbot = None

# Importamos el Trabajador Nutridor para el chat de ventas (Nido)
try:
    from trabajador_nutridor import TrabajadorNutridor
except ImportError:
    print("!!! ADVERTENCIA: No se encontró trabajador_nutridor.py. El chat del Nido estará desactivado.")
    TrabajadorNutridor = None

# --- CONFIGURACIÓN INICIAL ---
load_dotenv() # Asegura que las variables de entorno se carguen

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "autoneura-super-secret-key-2025")

# Convertidor de UUID para las URLs (Mantenemos esto para otras rutas que usen UUID)
class UUIDConverter(BaseConverter):
    def to_python(self, value): return uuid.UUID(value)
    def to_url(self, value): return str(value)

app.url_map.converters['uuid'] = UUIDConverter

# --- BLOQUE DE CONFIGURACIÓN DE IDIOMAS ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(basedir, 'translations')

def get_locale():
    if not request.accept_languages: return 'es'
    return request.accept_languages.best_match(['en', 'es'])

babel = Babel(app, locale_selector=get_locale)

@app.context_processor
def inject_get_locale():
    return dict(get_locale=get_locale)

# --- CONEXIÓN BASE DE DATOS Y API KEYS ---
DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# --- VARIABLES GLOBALES (SINGLETONS) ---
dashboard_brain = None # Cerebro para el Admin Dashboard
nutridor_brain = None  # Cerebro para el Nido (Clientes)

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    # Inicializamos el Nutridor una sola vez
    if TrabajadorNutridor:
        nutridor_brain = TrabajadorNutridor()

# --- HELPER DE BASE DE DATOS ---
def get_db_connection():
    """Crea una conexión segura a la base de datos."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"!!! ERROR CRÍTICO CONECTANDO A DB: {e}")
        return None

# --- RUTA DE HEALTHCHECK (PARA RAILWAY) ---
@app.route('/health')
def health_check():
    return "OK", 200

# --- RUTAS PRINCIPALES (VISTAS) ---
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

# --- API: CREACIÓN DE CAMPAÑA (Backend del Formulario) ---
@app.route('/api/crear-campana', methods=['POST'])
def crear_campana():
    """Recibe los datos del formulario frontend y crea la campaña en PostgreSQL."""
    conn = None
    try:
        data = request.json
        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "error": "Fallo de conexión a DB"}), 500
            
        cur = conn.cursor()

        # 1. Verificar/Crear Cliente Admin (Simplificado para MVP)
        # En el futuro, esto vendría del login de sesión real.
        cur.execute("SELECT id FROM clients WHERE email = 'admin@autoneura.com'")
        cliente_existente = cur.fetchone()
        
        client_id = None
        if cliente_existente:
            client_id = cliente_existente[0]
        else:
            # Crear cliente admin por defecto si no existe
            cur.execute("""
                INSERT INTO clients (email, full_name, is_active, daily_prospects_quota, balance)
                VALUES ('admin@autoneura.com', 'Admin Principal', TRUE, %s, 1000000.00)
                RETURNING id
            """, (int(data.get('prospectos_dia', 4)),))
            client_id = cur.fetchone()[0]
            conn.commit()

        # 2. Preparar Datos para el Orquestador/Analista
        desc_completa = f"{data.get('que_vende')}. Detalles: {data.get('descripcion')}. Enlace: {data.get('enlace_venta')}"

        # 3. Insertar Campaña
        cur.execute("""
            INSERT INTO campaigns (
                client_id, 
                campaign_name, 
                product_description, 
                target_audience, 
                product_type,
                search_languages, 
                geo_location,
                status,
                sales_link,
                whatsapp_contact,
                created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'active', %s, %s, NOW())
            RETURNING id
        """, (
            client_id,
            data.get('nombre'),
            desc_completa,
            data.get('a_quien'),
            data.get('tipo_producto'),
            data.get('idiomas'),
            data.get('ubicacion'),
            data.get('enlace_venta'),
            data.get('whatsapp')
        ))
        
        nueva_campana_id = cur.fetchone()[0]
        conn.commit()
        
        print(f">>> CAMPAÑA CREADA EXITOSAMENTE: {data.get('nombre')} (ID: {nueva_campana_id})")
        
        # Aquí es donde el Orquestador (en el otro proceso) detectará la campaña nueva
        
        return jsonify({"success": True, "message": "Campaña lanzada al Orquestador."})

    except Exception as e:
        print(f"Error creando campaña: {e}")
        if conn: conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        if conn: 
            cur.close()
            conn.close()

# --- RUTAS DEL SISTEMA PERSUASOR / NUTRIDOR (El Embudo) ---

@app.route('/ver-pre-nido/<string:token>')
def mostrar_pre_nido(token):
    """
    Paso 1 del Embudo: El prospecto hace clic en el enlace del email del Persuasor.
    Usamos <string:token> porque secrets.token_urlsafe genera texto, no UUID.
    """
    conn = get_db_connection()
    if not conn: return "Error de conexión con el servidor.", 500
    
    cur = conn.cursor()
    try:
        # Buscamos al prospecto por su TOKEN ÚNICO
        query = """
            SELECT id, business_name, contenido_generado 
            FROM prospects 
            WHERE token_acceso = %s
        """
        cur.execute(query, (token,))
        resultado = cur.fetchone()
        
        if resultado:
            pid, nombre_negocio, contenido_json = resultado
            
            # Extraemos los textos personalizados generados por el Persuasor
            # Si el JSON es nulo (por versión vieja), usamos defaults
            titulo = "Oportunidad Detectada"
            mensaje = "Hemos analizado tu negocio y tenemos una propuesta."
            
            if contenido_json:
                if isinstance(contenido_json, str):
                    import json
                    contenido_json = json.loads(contenido_json)
                
                titulo = contenido_json.get('prenido_titulo', titulo)
                mensaje = contenido_json.get('prenido_mensaje', mensaje)

            # Renderizamos la plantilla con los datos DB
            return render_template(
                'persuasor.html', 
                prospecto_id=pid, 
                nombre_negocio=nombre_negocio,
                titulo_personalizado=titulo,
                mensaje_personalizado=mensaje
            )
        else:
            return render_template('404.html'), 404 # O un mensaje simple si no tienes 404.html
            
    except Exception as e:
        print(f"Error en Pre-Nido: {e}")
        return "Ocurrió un error procesando tu solicitud.", 500
    finally:
        cur.close()
        conn.close()

@app.route('/generar-nido', methods=['POST'])
def generar_nido_y_entrar():
    """
    Paso 2 del Embudo: El prospecto ingresa su email en el Pre-Nido.
    Esto activa al Nutridor y muestra el Showroom.
    """
    email_usuario = request.form.get('email')
    prospecto_id = request.form.get('prospecto_id')
    
    if not email_usuario or not prospecto_id: 
        return "Faltan datos obligatorios.", 400

    conn = get_db_connection()
    if not conn: return "Error crítico DB", 500

    try:
        cur = conn.cursor()
        
        # 1. Actualizar Prospecto: Guardar email y cambiar estado
        cur.execute("""
            UPDATE prospects 
            SET captured_email = %s, 
                estado_prospecto = 'nutriendo', -- Activa al Nutridor asíncrono
                last_interaction_at = NOW()
            WHERE id = %s
            RETURNING business_name, token_acceso
        """, (email_usuario, prospecto_id))
        
        res = cur.fetchone()
        conn.commit()
        
        if not res: return "Prospecto no encontrado.", 404
        
        nombre_negocio, token_acceso = res
        
        # 2. Renderizar el Nido (Showroom)
        # Pasamos el token_acceso al frontend para que el Chat pueda usarlo
        return render_template(
            'nido_template.html',
            nombre_negocio=nombre_negocio,
            token_sesion=token_acceso, # CRÍTICO: El chat usará esto para saber quién es
            titulo_personalizado=f"Bienvenido al futuro de {nombre_negocio}",
            texto_contenido_de_valor="Aquí tienes la demostración interactiva de tu Agente IA."
        )

    except Exception as e:
        print(f"Error generando Nido: {e}")
        if conn: conn.rollback()
        return "Error interno del servidor.", 500
    finally:
        if conn:
            cur.close()
            conn.close()

@app.route('/api/chat-nido', methods=['POST'])
def chat_nido_api():
    """
    API del Chatbot de Ventas (El Nutridor en acción).
    Recibe el mensaje del usuario y el token de sesión.
    """
    data = request.json
    token = data.get('token')
    mensaje = data.get('mensaje')
    
    if not token or not mensaje:
        return jsonify({"respuesta": "Error de comunicación."}), 400

    if nutridor_brain:
        # Llamada al Trabajador Nutridor (Lógica real)
        respuesta_ia = nutridor_brain.responder_chat_nido(token, mensaje)
        return jsonify({"respuesta": respuesta_ia})
    else:
        return jsonify({"respuesta": "El sistema de IA se está reiniciando. Intenta en un momento."})

# --- CHATBOT DEL ADMIN DASHBOARD (Legacy / Soporte Técnico) ---
@app.route('/chat', methods=['POST'])
def chat_admin():
    global dashboard_brain
    try:
        # Lazy Loading del cerebro admin
        if dashboard_brain is None:
            print(">>> [main.py] Inicializando Cerebro Admin...")
            conn = get_db_connection()
            desc_campana = "Asistente AutoNeura"
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("SELECT product_description FROM campaigns LIMIT 1")
                    res = cur.fetchone()
                    if res: desc_campana = res[0]
                    conn.close()
                except: pass
            
            if create_chatbot:
                dashboard_brain = create_chatbot(descripcion_producto=desc_campana)
        
        user_message = request.json.get('message')
        if not user_message: return jsonify({"error": "Empty message"}), 400
        
        if dashboard_brain:
            response_text = dashboard_brain.invoke({"question": user_message})
            return jsonify({"response": response_text})
        else:
            return jsonify({"response": "Sistema en mantenimiento."})

    except Exception as e:
        print(f"Error en chat admin: {e}")
        return jsonify({"error": str(e)}), 500

# --- RUTAS DE VISUALIZACIÓN DIRECTA (PARA DEBUG) ---
@app.route('/confirmacion')
def mostrar_confirmacion(): return render_template('confirmacion.html')

# --- ARRANQUE DE LA APLICACIÓN ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    # En producción (Railway/Fly), debug debe ser False para estabilidad
    app.run(host='0.0.0.0', port=port, debug=False)
