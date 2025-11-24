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

# Definimos el Actor específico para espiar en Instagram (Triangulación)
# Usamos uno popular y eficiente, por ejemplo: "apify/instagram-profile-scraper"
ACTOR_ESPIA_ID = "apify/instagram-profile-scraper"

def obtener_prospectos_incompletos(campana_id):
    """
    Busca prospectos que:
    1. Pertenezcan a la campaña activa.
    2. NO tengan Email Y NO tengan WhatsApp/Teléfono (Prioridad absoluta).
    3. Tengan menos de 4 intentos de espionaje.
    4. No hayan sido descartados.
    """
    conn = None
    prospectos = []
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # SQL estricto: Solo trae lo que realmente necesitamos completar
        query = """
            SELECT id, business_name, social_profiles, source_bot_id, spy_attempts
            FROM prospects
            WHERE campana_id = %s
            AND email IS NULL 
            AND phone_number IS NULL
            AND (spy_attempts < 4 OR spy_attempts IS NULL)
            AND estado_prospecto != 'abandonado_por_espia'
            LIMIT 10; 
        """
        # LIMIT 10 para hacer lotes pequeños y controlar gastos
        
        cur.execute(query, (campana_id,))
        rows = cur.fetchall()
        
        for row in rows:
            prospectos.append({
                "id": row[0],
                "nombre": row[1],
                "socials": row[2] if row[2] else {},
                "source": row[3],
                "intentos": row[4] if row[4] else 0
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
    Define la estrategia: Si viene de TikTok, intentamos buscar el mismo user en Instagram.
    Retorna el 'username' objetivo para buscar en Instagram.
    """
    socials = prospecto["socials"]
    nombre_objetivo = prospecto["nombre"]
    username_busqueda = ""

    # ESTRATEGIA A: TRIANGULACIÓN TIKTOK -> INSTAGRAM
    if "tiktok" in socials:
        # Extraer username de la URL de tiktok (ej: tiktok.com/@juanperez -> juanperez)
        url_tiktok = socials["tiktok"]
        try:
            if "@" in url_tiktok:
                username_busqueda = url_tiktok.split("@")[1].split("?")[0].split("/")[0]
                logging.info(f"🎯 Objetivo detectado (Origen TikTok): Buscando @{username_busqueda} en Instagram.")
                return username_busqueda
        except:
            pass
    
    # ESTRATEGIA B: NOMBRE DIRECTO (Si no hay link de TikTok)
    # Intentamos buscar por el nombre del negocio pegado
    if not username_busqueda and nombre_objetivo:
        username_busqueda = nombre_objetivo.replace(" ", "").lower()
        logging.info(f"🎯 Objetivo detectado (Nombre): Probando búsqueda directa de @{username_busqueda} en Instagram.")
        return username_busqueda

    return None

def ejecutar_espionaje_apify(username_objetivo):
    """
    Ejecuta el scraper de Instagram con CONFIGURACIÓN DE AHORRO EXTREMO.
    """
    if not username_objetivo:
        return None

    client = ApifyClient(APIFY_TOKEN)
    
    # --- CONFIGURACIÓN DE AHORRO (CRÍTICO) ---
    # Solo buscamos la bio y el email. Nada de fotos, nada de posts.
    run_input = {
        "usernames": [username_objetivo],
        "resultsLimit": 1,
        # AHORRO:
        "downloadImages": False,      # NO bajar fotos
        "downloadVideos": False,      # NO bajar videos
        "scrapePosts": False,         # NO leer posts (ahorra mucho tiempo y proxy)
        "scrapeStories": False,       # NO ver historias
        "scrapeHighlights": False,    # NO ver destacados
    }

    try:
        logging.info(f"🕵️ Lanzando Agente Espía hacia Instagram: @{username_objetivo}")
        run = client.actor(ACTOR_ESPIA_ID).call(run_input=run_input)
        
        if not run or run.get('status') != 'SUCCEEDED':
            logging.warning("El Agente Espía no pudo entrar o falló.")
            return None

        dataset_id = run["defaultDatasetId"]
        items = client.dataset(dataset_id).list_items().items
        
        if items:
            return items[0] # Retornamos el perfil encontrado
        else:
            return None

    except Exception as e:
        logging.error(f"Error técnico en Apify: {e}")
        return None

def guardar_hallazgos(prospecto_id, datos_encontrados, intentos_actuales):
    """
    Actualiza la base de datos con la información rescatada o incrementa el contador de fallos.
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    nuevo_email = None
    nuevo_telefono = None
    nueva_bio = None
    
    exito = False

    if datos_encontrados:
        # Intentar extraer email del campo 'businessEmail' o de la 'biography'
        nuevo_email = datos_encontrados.get("businessEmail")
        if not nuevo_email:
            # Lógica simple para buscar '@' en la bio si no hay businessEmail
            bio = datos_encontrados.get("biography", "")
            if "@" in bio:
                palabras = bio.split()
                for p in palabras:
                    if "@" in p and "." in p:
                        nuevo_email = p.strip()
                        break
        
        # Intentar extraer teléfono
        nuevo_telefono = datos_encontrados.get("businessPhoneNumber")
        
        nueva_bio = datos_encontrados.get("biography")

    # SQL Dinámico: Solo actualizamos si encontramos algo
    try:
        if nuevo_email or nuevo_telefono:
            logging.info(f"✅ ¡ÉXITO! Datos recuperados para ID {prospecto_id}: Email={nuevo_email}, Tel={nuevo_telefono}")
            cur.execute("""
                UPDATE prospects
                SET email = COALESCE(email, %s),
                    phone_number = COALESCE(phone_number, %s),
                    puntos_de_dolor = %s, -- Guardamos la bio como info extra para el analista
                    spy_attempts = spy_attempts + 1,
                    updated_at = NOW()
                WHERE id = %s
            """, (nuevo_email, nuevo_telefono, nueva_bio, prospecto_id))
            exito = True
        else:
            logging.info(f"❌ Misión fallida. No se encontraron datos públicos de contacto para ID {prospecto_id}.")
            
            # Si llegamos al límite de 4 intentos, lo marcamos para no gastar más
            nuevo_estado = 'cazado' # Mantiene estado original
            if intentos_actuales + 1 >= 4:
                nuevo_estado = 'abandonado_por_espia'
                logging.warning(f"⚠️ ID {prospecto_id} ha alcanzado el límite de intentos. Se abandona.")
            
            cur.execute("""
                UPDATE prospects
                SET spy_attempts = COALESCE(spy_attempts, 0) + 1,
                    estado_prospecto = %s
                WHERE id = %s
            """, (nuevo_estado, prospecto_id))

        conn.commit()
    except Exception as e:
        logging.error(f"Error guardando en DB: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
    return exito

# --- FUNCIÓN PRINCIPAL ORQUESTADA ---

def trabajar_espia(campana_id, limite_diario_cliente=4):
    """
    El Orquestador llama a esta función.
    Calcula el límite de ejecuciones basado en el plan del cliente.
    """
    logging.info(f"🕵️ INICIANDO TURNO DE ESPÍA | Campaña: {campana_id}")
    
    # Regla de Negocio: Máximo 4 intentos por prospecto del plan diario.
    # Si el plan es 4 prospectos/día, permitimos hasta 16 ejecuciones del espía.
    MAX_EJECUCIONES_HOY = limite_diario_cliente * 4
    
    # 1. Obtener objetivos (los que NO tienen datos)
    objetivos = obtener_prospectos_incompletos(campana_id)
    
    if not objetivos:
        logging.info("💤 No hay prospectos incompletos que requieran espionaje. Durmiendo.")
        return

    contador_ejecuciones = 0

    for prospecto in objetivos:
        if contador_ejecuciones >= MAX_EJECUCIONES_HOY:
            logging.info("🛑 Se alcanzó el límite de presupuesto diario para el Espía. Deteniendo.")
            break

        # 2. Definir Username para buscar (Triangulación)
        username_target = triangulacion_identidad(prospecto)
        
        if username_target:
            # 3. Ejecutar Apify (Gasto de dinero)
            datos = ejecutar_espionaje_apify(username_target)
            contador_ejecuciones += 1
            
            # 4. Guardar resultados
            guardar_hallazgos(prospecto["id"], datos, prospecto["intentos"])
        else:
            logging.info(f"⏭️ No se pudo determinar un username para ID {prospecto['id']}. Saltando.")
            # Opcional: Incrementar contador de intentos para no quedarse en bucle infinito
            guardar_hallazgos(prospecto["id"], None, prospecto["intentos"])

    logging.info(f"🏁 Turno Espía finalizado. Ejecuciones realizadas: {contador_ejecuciones}/{MAX_EJECUCIONES_HOY}")

# --- ENTRY POINT (PRUEBA) ---
if __name__ == "__main__":
    # ID de campaña para probar
    CAMPAÑA_TEST = "tu-uuid-aqui" 
    print(">> Iniciando prueba manual de trabajador_espia.py")
    # trabajar_espia(CAMPAÑA_TEST)
