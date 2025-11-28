import os
import json
import logging
import datetime
from apify_client import ApifyClient
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

# --- CONFIGURACIÓN ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - ESPIA - %(levelname)s - %(message)s')

APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")

# --- PRESUPUESTO FINANCIERO ESTRICTO ---
PRESUPUESTO_ESPIA_POR_PROSPECTO = 1.50  # Dólares por lead contratado al MES
COSTO_APIFY_INSTAGRAM_PERFIL = 0.005    # Costo aproximado por consulta

# Actor Apify Oficial
ACTOR_ESPIA_ID = "apify/instagram-scraper" 

# --- 1. AUDITORIA GRATUITA (COSTO $0) ---

def procesar_gratuitos(campana_id):
    """
    Revisa la base de datos y promueve a 'espiado' a todos los que 
    YA tienen datos de contacto, sin gastar dinero en Apify.
    """
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Actualización Masiva:
        # Si está 'cazado' Y tiene (Email O Teléfono) -> Pasa directo a 'espiado'
        query = """
            UPDATE prospects
            SET status = 'espiado',
                updated_at = NOW()
            WHERE campaign_id = %s
            AND status = 'cazado'
            AND (captured_email IS NOT NULL OR phone_number IS NOT NULL);
        """
        cur.execute(query, (campana_id,))
        cantidad = cur.rowcount
        conn.commit()
        
        if cantidad > 0:
            logging.info(f"✨ AUDITORÍA GRATUITA: {cantidad} prospectos ya tenían datos. Promovidos a 'espiado' sin costo.")
        
        cur.close()
    except Exception as e:
        logging.error(f"Error en auditoría gratuita: {e}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close()

# --- 2. CEREBRO FINANCIERO (BOZAL) ---

def calcular_cupo_diario_espia(campana_id, limite_diario_contratado):
    if not limite_diario_contratado or limite_diario_contratado < 1:
        limite_diario_contratado = 4

    # 5 leads * $1.50 = $7.50 USD mes
    presupuesto_mensual = limite_diario_contratado * PRESUPUESTO_ESPIA_POR_PROSPECTO
    # $7.50 / 30 = $0.25 USD diario
    presupuesto_diario = presupuesto_mensual / 30.0
    # $0.25 / $0.005 = ~50 consultas
    consultas_permitidas_hoy = int(presupuesto_diario / COSTO_APIFY_INSTAGRAM_PERFIL)
    
    if consultas_permitidas_hoy < 3: consultas_permitidas_hoy = 3
    
    return consultas_permitidas_hoy

# --- 3. TRIANGULACIÓN Y APIFY ---

def triangular_username(prospecto):
    socials = prospecto.get("social_profiles", {}) or {}
    nombre_negocio = prospecto.get("business_name")
    
    # Intento 1: TikTok Username
    if "tiktok" in socials:
        url = socials["tiktok"]
        try:
            parts = url.split('@')
            if len(parts) > 1:
                return parts[1].split('/')[0].split('?')[0].strip()
        except: pass

    # Intento 2: Nombre limpio
    if nombre_negocio:
        return "".join(e for e in nombre_negocio if e.isalnum()).lower()

    return None

def espiar_en_instagram(username):
    client = ApifyClient(APIFY_TOKEN)
    run_input = {
        "usernames": [username],
        "resultsLimit": 1,
        "resultsType": "details",
        "downloadImages": False,
        "downloadVideos": False,
        "scrapePosts": False,
        "scrapeStories": False,
        "proxy": {"useApifyProxy": True}
    }

    try:
        logging.info(f"🕵️ Gastando saldo en Instagram: @{username}")
        run = client.actor(ACTOR_ESPIA_ID).call(run_input=run_input)
        
        if not run or run.get('status') != 'SUCCEEDED': return None

        dataset_id = run["defaultDatasetId"]
        items = client.dataset(dataset_id).list_items().items
        return items[0] if items else None

    except Exception as e:
        logging.error(f"❌ Fallo Apify: {e}")
        return None

# --- 4. FUNCIÓN PRINCIPAL ---

def ejecutar_espia(campana_id, limite_diario_contratado=4):
    
    # PASO 1: Procesar los GRATIS (Esto se ejecuta SIEMPRE, haya dinero o no)
    procesar_gratuitos(campana_id)

    # PASO 2: Chequeo Financiero para el resto
    cupo_hoy = calcular_cupo_diario_espia(campana_id, limite_diario_contratado)
    logging.info(f"💰 Cupo Apify Restante Hoy: {cupo_hoy} perfiles.")

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Buscamos SOLO los que realmente faltan (Siguen cazados y vacíos)
    query = """
        SELECT id, business_name, social_profiles, source_bot_id
        FROM prospects
        WHERE campaign_id = %s
        AND status = 'cazado' 
        AND captured_email IS NULL 
        AND phone_number IS NULL
        LIMIT %s;
    """
    cur.execute(query, (campana_id, cupo_hoy))
    objetivos = cur.fetchall()

    if not objetivos:
        logging.info("💤 Todo limpio. No hay nada pendiente que requiera gasto.")
        cur.close()
        conn.close()
        return

    count_exitos = 0
    
    for row in objetivos:
        pid, bname, socials, source = row
        prospecto_dict = {"business_name": bname, "social_profiles": socials}
        
        target_user = triangular_username(prospecto_dict)
        datos_nuevos = None
        
        if target_user:
            datos_nuevos = espiar_en_instagram(target_user)
        
        # Extracción de datos
        nuevo_email = None
        nuevo_phone = None
        
        if datos_nuevos:
            nuevo_email = datos_nuevos.get("businessEmail") or datos_nuevos.get("email")
            nuevo_phone = datos_nuevos.get("businessPhoneNumber") or datos_nuevos.get("phone")
            
            if not nuevo_email and datos_nuevos.get("biography"):
                bio = datos_nuevos["biography"]
                for w in bio.split():
                    if "@" in w and "." in w:
                        nuevo_email = w
                        break

        # Guardado
        if nuevo_email or nuevo_phone:
            logging.info(f"✅ PAGADO Y ENCONTRADO ID {pid}: {nuevo_email}")
            cur.execute("""
                UPDATE prospects 
                SET captured_email = COALESCE(captured_email, %s),
                    phone_number = COALESCE(phone_number, %s),
                    status = 'espiado',
                    updated_at = NOW()
                WHERE id = %s
            """, (nuevo_email, nuevo_phone, pid))
            count_exitos += 1
        else:
            # Si pagamos y fallamos, lo marcamos descartado
            logging.info(f"❌ Pagado sin éxito ID {pid}. Descartado.")
            cur.execute("UPDATE prospects SET status = 'descartado_espia', updated_at = NOW() WHERE id = %s", (pid,))
            
        conn.commit()

    cur.close()
    conn.close()
    logging.info(f"🏁 Turno Espía finalizado. Invertidos en Apify: {len(objetivos)}")
