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
COSTO_APIFY_INSTAGRAM_PERFIL = 0.005    # Costo aproximado por consulta (5 USD / 1000)

# Actor Apify Oficial y Barato para Instagram
ACTOR_ESPIA_ID = "apify/instagram-scraper" 

# --- 1. CEREBRO FINANCIERO (BOZAL) ---

def calcular_cupo_diario_espia(campana_id, limite_diario_contratado):
    """
    Calcula cuántos perfiles podemos espiar HOY basándonos en el presupuesto de $1.50/mes.
    """
    if not limite_diario_contratado or limite_diario_contratado < 1:
        limite_diario_contratado = 4

    # 1. Presupuesto Mensual Total del Espía
    # Ej: 5 leads * $1.50 = $7.50 USD al mes
    presupuesto_mensual = limite_diario_contratado * PRESUPUESTO_ESPIA_POR_PROSPECTO
    
    # 2. Presupuesto Diario
    # Ej: $7.50 / 30 = $0.25 USD diarios
    presupuesto_diario = presupuesto_mensual / 30.0
    
    # 3. Convertir Dinero a "Consultas Apify"
    # Ej: $0.25 / $0.005 = 50 consultas diarias permitidas
    consultas_permitidas_hoy = int(presupuesto_diario / COSTO_APIFY_INSTAGRAM_PERFIL)
    
    # Mínimo de seguridad para que valga la pena despertar
    if consultas_permitidas_hoy < 3: consultas_permitidas_hoy = 3
    
    return consultas_permitidas_hoy

# --- 2. LÓGICA DE TRIANGULACIÓN ---

def triangular_username(prospecto):
    """
    Intenta deducir el username de Instagram.
    Prioridad: Username de TikTok -> Nombre del Negocio limpio.
    """
    socials = prospecto.get("social_profiles", {}) or {}
    nombre_negocio = prospecto.get("business_name")
    
    # 1. Si viene de TikTok, el username suele ser el mismo
    if "tiktok" in socials:
        url = socials["tiktok"]
        try:
            # Extraer 'usuario' de tiktok.com/@usuario
            parts = url.split('@')
            if len(parts) > 1:
                username = parts[1].split('/')[0].split('?')[0]
                return username.strip()
        except:
            pass

    # 2. Si viene de Maps/Google, intentamos con el nombre del negocio
    # Eliminamos espacios y caracteres raros
    if nombre_negocio:
        clean_name = "".join(e for e in nombre_negocio if e.isalnum()).lower()
        return clean_name

    return None

# --- 3. EJECUCIÓN APIFY (MODO AHORRO) ---

def espiar_en_instagram(username):
    """
    Consulta Apify con configuración de AHORRO MÁXIMO.
    """
    client = ApifyClient(APIFY_TOKEN)
    
    run_input = {
        "usernames": [username], # Usamos usernames directo, es más barato que búsqueda
        "resultsLimit": 1,
        "resultsType": "details",
        # --- AHORRO EXTREMO ---
        "downloadImages": False,
        "downloadVideos": False,
        "scrapePosts": False,       # NO bajar posts (ahorra mucho)
        "scrapeStories": False,
        "proxy": {"useApifyProxy": True}
    }

    try:
        logging.info(f"🕵️ Consultando Instagram para: @{username}")
        run = client.actor(ACTOR_ESPIA_ID).call(run_input=run_input)
        
        if not run or run.get('status') != 'SUCCEEDED':
            return None

        dataset_id = run["defaultDatasetId"]
        items = client.dataset(dataset_id).list_items().items
        
        if items:
            return items[0]
        return None

    except Exception as e:
        logging.error(f"❌ Fallo Apify: {e}")
        return None

# --- 4. FUNCIÓN PRINCIPAL ---

def ejecutar_espia(campana_id, limite_diario_contratado=4):
    
    # 1. Chequeo Financiero
    cupo_hoy = calcular_cupo_diario_espia(campana_id, limite_diario_contratado)
    logging.info(f"💰 PRESUPUESTO ESPÍA HOY: {cupo_hoy} perfiles.")

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # 2. Buscar Objetivos (Solo los que NO tienen contacto y NO han sido descartados)
    # Priorizamos los cazados recientemente
    query = """
        SELECT id, business_name, social_profiles, source_bot_id
        FROM prospects
        WHERE campaign_id = %s
        AND status = 'cazado' 
        AND (captured_email IS NULL AND phone_number IS NULL)
        LIMIT %s;
    """
    cur.execute(query, (campana_id, cupo_hoy))
    objetivos = cur.fetchall()

    if not objetivos:
        logging.info("💤 No hay prospectos sin contacto para espiar hoy.")
        cur.close()
        conn.close()
        return

    count_exitos = 0
    count_fallos = 0

    for row in objetivos:
        pid, bname, socials, source = row
        prospecto_dict = {"business_name": bname, "social_profiles": socials}
        
        # 3. Triangulación
        target_user = triangular_username(prospecto_dict)
        
        datos_nuevos = None
        if target_user:
            datos_nuevos = espiar_en_instagram(target_user)
        
        # 4. Procesar Hallazgos
        nuevo_email = None
        nuevo_phone = None
        
        if datos_nuevos:
            nuevo_email = datos_nuevos.get("businessEmail") or datos_nuevos.get("email")
            nuevo_phone = datos_nuevos.get("businessPhoneNumber") or datos_nuevos.get("phone")
            
            # Si no hay email en campos directos, buscar en biografía
            if not nuevo_email and datos_nuevos.get("biography"):
                bio = datos_nuevos["biography"]
                words = bio.split()
                for w in words:
                    if "@" in w and "." in w: # Detección rústica de email
                        nuevo_email = w
                        break

        # 5. Guardar Resultados en DB
        if nuevo_email or nuevo_phone:
            logging.info(f"✅ CONTACTO ENCONTRADO ID {pid}: {nuevo_email} | {nuevo_phone}")
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
            # Si no encontramos nada, lo marcamos 'descartado_espia' para no volver a gastar
            # O 'espiado' (sin éxito) para que pase al siguiente worker si aplica
            logging.info(f"❌ Sin datos para ID {pid}. Marcando descartado.")
            cur.execute("""
                UPDATE prospects 
                SET status = 'descartado_espia', 
                    updated_at = NOW()
                WHERE id = %s
            """, (pid,))
            count_fallos += 1
            
        conn.commit()

    cur.close()
    conn.close()
    logging.info(f"🏁 RONDA FINALIZADA. Éxitos: {count_exitos} | Descartados: {count_fallos}")
