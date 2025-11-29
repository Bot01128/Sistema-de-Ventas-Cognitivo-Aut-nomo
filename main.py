import os
import psycopg2
import json
import google.generativeai as genai
import uuid
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_babel import Babel, gettext
from psycopg2.extras import Json
from werkzeug.routing import BaseConverter
from dotenv import load_dotenv

# --- IMPORTACIÓN DE MÓDULOS PROPIOS ---
try:
    from cerebro_dashboard import create_chatbot
except ImportError:
    create_chatbot = None

try:
    from trabajador_nutridor import TrabajadorNutridor
except ImportError:
    TrabajadorNutridor = None

# --- CONFIGURACIÓN INICIAL ---
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "autoneura-super-secret-key-2025")

class UUIDConverter(BaseConverter):
    def to_python(self, value): return uuid.UUID(value)
    def to_url(self, value): return str(value)

app.url_map.converters['uuid'] = UUIDConverter

# --- IDIOMAS ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(basedir, 'translations')

def get_locale():
    return request.accept_languages.best_match(['en', 'es']) or 'es'

babel = Babel(app, locale_selector=get_locale)

@app.context_processor
def inject_get_locale():
    return dict(get_locale=get_locale, _=gettext)

# --- CONEXIÓN DB Y API ---
DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

dashboard_brain = None
nutridor_brain = None

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    if TrabajadorNutridor:
        nutridor_brain = TrabajadorNutridor()

def get_db_connection():
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"Error DB: {e}")
        return None

# --- RUTAS PRINCIPALES ---
@app.route('/')
def home(): return render_template('dashboard.html')

@app.route('/cliente')
def client_dashboard(): return render_template('client_dashboard.html')

@app.route('/mis-clientes')
def mis_clientes(): return render_template('mis_clientes.html')

@app.route('/admin')
def admin_dashboard(): return render_template('admin_dashboard.html')

@app.route('/admin/taller')
def admin_taller(): return render_template('admin_taller.html')

# --- API: DATOS DEL DASHBOARD ---
@app.route('/api/dashboard-data', methods=['GET'])
def obtener_datos_dashboard():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "No DB"}), 500
    
    try:
        cur = conn.cursor()
        client_email = 'admin@autoneura.com' 
        
        cur.execute("""
            SELECT 
                COUNT(p.id) as total,
                COUNT(p.id) FILTER (WHERE p.nurture_interactions_count >= 3) as calificados
            FROM prospects p
            JOIN campaigns c ON p.campaign_id = c.id
            JOIN clients cl ON c.client_id = cl.id
            WHERE cl.email = %s
        """, (client_email,))
        kpis = cur.fetchone()
        total_prospectos = kpis[0] or 0
        total_calificados = kpis[1] or 0
        tasa_conversion = round((total_calificados / total_prospectos * 100), 1) if total_prospectos > 0 else 0

        cur.execute("""
            SELECT 
                c.campaign_name, 
                c.created_at, 
                c.status,
                COUNT(p.id) as encontrados,
                COUNT(p.id) FILTER (WHERE p.nurture_interactions_count >= 3) as leads
            FROM campaigns c
            JOIN clients cl ON c.client_id = cl.id
            LEFT JOIN prospects p ON c.id = p.campaign_id
            WHERE cl.email = %s
            GROUP BY c.id
            ORDER BY c.created_at DESC
        """, (client_email,))
        
        campanas = []
        for row in cur.fetchall():
            campanas.append({
                "nombre": row[0],
                "fecha": row[1].strftime('%Y-%m-%d') if row[1] else "-",
                "estado": row[2],
                "encontrados": row[3],
                "calificados": row[4]
            })

        return jsonify({
            "kpis": {
                "total": total_prospectos,
                "calificados": total_calificados,
                "tasa": f"{tasa_conversion}%"
            },
            "campanas": campanas
        })

    except Exception as e:
        print(f"Error API Dashboard: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

# --- API: CREAR CAMPAÑA (CORREGIDO: AHORA GUARDA LOS DATOS NUEVOS) ---
@app.route('/api/crear-campana', methods=['POST'])
def crear_campana():
    conn = get_db_connection()
    if not conn: return jsonify({"success": False}), 500
    try:
        d = request.json
        cur = conn.cursor()
        
        # 1. Obtener o Crear Cliente Admin
        cur.execute("SELECT id FROM clients WHERE email = 'admin@autoneura.com'")
        res = cur.fetchone()
        if not res:
            cur.execute("INSERT INTO clients (email, full_name, plan_type, plan_cost) VALUES ('admin@autoneura.com', 'Admin', 'starter', 149.00) RETURNING id")
            cid = cur.fetchone()[0]
            conn.commit()
        else:
            cid = res[0]

        # 2. Preparar Datos (Incluyendo los nuevos campos estratégicos)
        desc = f"{d.get('que_vende')}. {d.get('descripcion')}"
        
        # Recogemos los campos nuevos del formulario HTML
        ticket = d.get('ticket_producto')
        competidores = d.get('competidores_principales')
        cta = d.get('objetivo_cta')
        dolores = d.get('dolores_pain_points')
        tono = d.get('tono_marca')
        red_flags = d.get('red_flags')
        
        # Guardamos en la base de datos (INSERT actualizado)
        cur.execute("""
            INSERT INTO campaigns (
                client_id, campaign_name, product_description, target_audience, 
                product_type, search_languages, geo_location,
                ticket_price, competitors, cta_goal, pain_points_defined, tone_voice, red_flags,
                status, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'active', NOW())
            RETURNING id
        """, (
            cid, d.get('nombre'), desc, d.get('a_quien'), 
            d.get('tipo_producto'), d.get('idiomas'), d.get('ubicacion'),
            ticket, competidores, cta, dolores, tono, red_flags
        ))
        
        nid = cur.fetchone()[0]
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        if conn: conn.rollback()
        # Logueamos el error para verlo en Railway si falla
        print(f"ERROR CREANDO CAMPAÑA: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()

# --- RUTAS DE NIDO ---
@app.route('/ver-pre-nido/<string:token>')
def mostrar_pre_nido(token):
    conn = get_db_connection()
    if not conn: return "Error DB", 500
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, business_name, generated_content FROM prospects WHERE access_token = %s", (token,))
            res = cur.fetchone()
            if res:
                content = res[2] if res[2] else {}
                if isinstance(content, str): content = json.loads(content)
                return render_template('persuasor.html', prospecto_id=res[0], nombre_negocio=res[1], 
                                     titulo_personalizado=content.get('prenido_titulo', 'Hola'),
                                     mensaje_personalizado=content.get('prenido_mensaje', 'Bienvenido'))
            return "Enlace no válido", 404
    finally:
        conn.close()

@app.route('/generar-nido', methods=['POST'])
def generar_nido_y_entrar():
    email = request.form.get('email')
    pid = request.form.get('prospecto_id')
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE prospects SET captured_email = %s, status = 'nutriendo', last_interaction_at = NOW()
                WHERE id = %s RETURNING business_name, access_token
            """, (email, pid))
            res = cur.fetchone()
            conn.commit()
            if res:
                return render_template('nido_template.html', nombre_negocio=res[0], token_sesion=res[1], 
                                     titulo_personalizado=f"Bienvenido {res[0]}", texto_contenido_de_valor="Demo")
            return "Error", 404
    finally:
        conn.close()

@app.route('/api/chat-nido', methods=['POST'])
def chat_nido_api():
    d = request.json
    if nutridor_brain:
        return jsonify({"respuesta": nutridor_brain.responder_chat_nido(d.get('token'), d.get('mensaje'))})
    return jsonify({"respuesta": "Conectando..."})

# --- RUTAS DEBUG ---
@app.route('/ver-pre-nido')
def debug_pre(): return render_template('persuasor.html', prospecto_id="TEST", nombre_negocio="Demo", titulo_personalizado="Demo", mensaje_personalizado="Demo")

@app.route('/ver-nido')
def debug_nido(): return render_template('nido_template.html', nombre_negocio="Demo", token_sesion="TEST", titulo_personalizado="Demo", texto_contenido_de_valor="Demo")

@app.route('/chat', methods=['POST'])
def chat_admin():
    global dashboard_brain
    if not dashboard_brain and create_chatbot: dashboard_brain = create_chatbot()
    if dashboard_brain: return jsonify({"response": dashboard_brain.invoke({"question": request.json.get('message')})})
    return jsonify({"response": "Mantenimiento"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
