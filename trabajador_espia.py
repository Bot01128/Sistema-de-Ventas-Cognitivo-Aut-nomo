import os
import json
import logging
from apify_client import ApifyClient
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

# --- CONFIGURACIÓN ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - ESPIA - %(levelname)s - %(message)s')

APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")

# Definimos el Actor específico para espiar en Instagram (Triangulación)
ACTOR_ESPIA_ID = "apify/instagram-scraper" # Cambiado a scraper más genérico y robusto

def obtener_prospectos_incompletos(campana_id):
    """
    Busca prospectos que necesitan datos de contacto.
    TABLAS EN INGLÉS: 'campaigns', 'prospects'
    """
    conn = None
    prospectos = []
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # SQL CORREGIDO (INGLÉS)
        # Buscamos prospectos activos de la campaña que no tengan email/teléfono
        # y que no hayan excedido los intentos de espionaje.
        # Usamos 'raw_data' para chequear intentos si no hay columna dedicada
        query = """
            SELECT id, business_name, social_profiles, source_bot_id
            FROM prospects
            WHERE campaign_id = %s
            AND captured_email IS NULL 
            AND phone_number IS NULL
            AND status != 'abandonado_por_espia'
            LIMIT 5; 
        """
        
        cur.execute(query, (campana_id,))
        rows = cur.fetchall()
        
        for row in rows:
            prospectos.append({
                "id": row[0],
                "nombre": row[1],
                "socials": row[2] if row[2] else {},
                "source": row[3]
            })
            
        cur.close()
        return prospectos

    except Exception as e:
        logging.error(f"Error buscando objetivos para espiar: {e}")
        return []
    finally:
        if conn: conn.close()

def triangulacion_identidad(prospecto):
    """
    Intenta adivinar el usuario de Instagram basado en TikTok o el Nombre.
    """
    socials = prospecto["socials"]
    nombre_objetivo = prospecto["nombre"]
    username_busqueda = ""

    # ESTRATEGIA A: Si ya tenemos TikTok, usamos ese username
    if "tiktok" in socials:
        url_tiktok = socials["tiktok"]
        try:
            if "@" in url_tiktok:
                username_busqueda = url_tiktok.split("@")[1].split("?")[0].split("/")[0]
                logging.info(f"🎯 Objetivo (TikTok -> Instagram): @{username_busqueda}")
                return username_busqueda
        except: pass
    
    # ESTRATEGIA B: Usar el nombre del negocio sin espacios
    if not username_busqueda and nombre_objetivo:
        username_busqueda = nombre_objetivo.replace(" ", "").lower()
        logging.info(f"🎯 Objetivo (Nombre Directo): @{username_busqueda}")
        return username_busqueda

    return None

def ejecutar_espionaje_apify(username_objetivo):
    """
    Ejecuta el scraper de Instagram con AHORRO DE COSTOS.
    """
    if not username_objetivo: return None

    client = ApifyClient(APIFY_TOKEN)
    
    # --- CONFIGURACIÓN DE AHORRO ---
    run_input = {
        "search": username_objetivo,
        "searchType": "user",
        "resultsLimit": 1,
        "resultsType": "details", # Solo detalles, no posts
        # "searchLimit": 1 
    }

    try:
        logging.info(f"🕵️ Espiando en Instagram: {username_objetivo}")
        run = client.actor(ACTOR_ESPIA_ID).call(run_input=run_input)
        
        if not run or run.get('status') != 'SUCCEEDED':
            logging.warning("El Espía falló en Apify.")
            return None

        dataset_id = run["defaultDatasetId"]
        items = client.dataset(dataset_id).list_items().items
        
        if items:
            return items[0] 
        else:
            return None

    except Exception as e:
        logging.error(f"Error técnico Apify: {e}")
        return None

def guardar_hallazgos(prospecto_id, datos_encontrados):
    """
    Guarda los datos encontrados en la DB (INGLÉS).
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    nuevo_email = None
    nuevo_telefono = None
    exito = False

    if datos_encontrados:
        # Intentamos sacar email de la bio o campos públicos
        nuevo_email = datos_encontrados.get("publicEmail")
        if not nuevo_email:
            # Buscar @ en la bio manualmente
            bio = datos_encontrados.get("biography", "")
            if "@" in bio:
                for p in bio.split():
                    if "@" in p and "." in p:
                        nuevo_email = p.strip()
                        break
        
        # Telefono (si es cuenta business)
        nuevo_telefono = datos_encontrados.get("contactPhoneNumber")

    try:
        if nuevo_email or nuevo_telefono:
            logging.info(f"✅ ¡ÉXITO! Datos recuperados ID {prospecto_id}: {nuevo_email} | {nuevo_telefono}")
            # Actualizamos captured_email si no había, o phone_number
            cur.execute("""
                UPDATE prospects
                SET captured_email = COALESCE(captured_email, %s),
                    phone_number = COALESCE(phone_number, %s),
                    updated_at = NOW()
                WHERE id = %s
            """, (nuevo_email, nuevo_telefono, prospecto_id))
            exito = True
        else:
            logging.info(f"❌ Misión fallida para ID {prospecto_id}. No hay datos públicos.")
            # Marcamos para no insistir
            cur.execute("UPDATE prospects SET status = 'abandonado_por_espia' WHERE id = %s", (prospecto_id,))

        conn.commit()
    except Exception as e:
        logging.error(f"Error guardando hallazgos: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
    return exito

# --- FUNCIÓN PRINCIPAL ---

def trabajar_espia(campana_id, limite_diario=4):
    logging.info(f"🕵️ INICIANDO TURNO DE ESPÍA | Campaña: {campana_id}")
    
    objetivos = obtener_prospectos_incompletos(campana_id)
    
    if not objetivos:
        logging.info("💤 Nada que espiar.")
        return

    # Límite de seguridad para no gastar todo el dinero
    max_intentos = limite_diario * 2 
    intentos = 0

    for prospecto in objetivos:
        if intentos >= max_intentos: break

        target = triangulacion_identidad(prospecto)
        if target:
            datos = ejecutar_espionaje_apify(target)
            guardar_hallazgos(prospecto["id"], datos)
            intentos += 1
        else:
            # Si no podemos adivinar el usuario, lo marcamos como abandonado
            # Para no quedarnos pegados en el mismo
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute("UPDATE prospects SET status = 'abandonado_por_espia' WHERE id = %s", (prospecto["id"],))
            conn.commit()
            conn.close()

    logging.info("🏁 Turno Espía finalizado.")
