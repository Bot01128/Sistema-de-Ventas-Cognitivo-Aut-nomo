import os
import json
import logging
from apify_client import ApifyClient
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

# --- CONFIGURACIÓN INICIAL ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - CAZADOR - %(levelname)s - %(message)s')

APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")

# --- LÓGICA DE INTELIGENCIA (EL ARSENAL) ---

def consultar_arsenal(plataforma_objetivo, tipo_producto):
    """
    Consulta la tabla 'bot_arsenal' para obtener el mejor 'Actor'.
    """
    logging.info(f"🔎 Consultando Arsenal para: Plataforma={plataforma_objetivo}, Producto={tipo_producto}")
    
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # En la nueva DB, 'target_type' define si es Local Business, Entrepreneur, etc.
        # Adaptamos la lógica simple para que elija el bot correcto por plataforma
        query = """
            SELECT actor_id, name 
            FROM bot_arsenal 
            WHERE platform = %s 
            AND is_active = TRUE
            LIMIT 1;
        """
        
        cur.execute(query, (plataforma_objetivo,))
        resultado = cur.fetchone()
        
        cur.close()
        
        if resultado:
            logging.info(f"✅ Bot Seleccionado: {resultado[1]} (ID: {resultado[0]})")
            return {"nombre": resultado[1], "actor_id": resultado[0]}
        else:
            # Fallback: Si no encuentra uno específico, usa Google Maps por defecto
            logging.warning("⚠️ No se encontró bot específico. Usando Google Maps por defecto.")
            return {"nombre": "Hunter Gmaps", "actor_id": "compass/crawler-google-places"}

    except Exception as e:
        logging.error(f"❌ Error conectando al Arsenal: {e}")
        return {"nombre": "Hunter Gmaps", "actor_id": "compass/crawler-google-places"} # Fallback seguro
    finally:
        if conn: conn.close()

# --- LÓGICA DE AHORRO Y EJECUCIÓN (INPUTS) ---

def preparar_input_blindado(actor_id, busqueda, ubicacion, max_items):
    """
    Configura los parámetros del Bot asegurando el AHORRO DE COSTOS.
    """
    logging.info(f"⚙️ Configurando parámetros de ahorro para: {actor_id}")

    # 1. Google Maps (Compass o Apify Oficial)
    if "google-maps" in actor_id or "google-places" in actor_id:
        return {
            "searchStringsArray": [busqueda],
            "locationQuery": ubicacion,
            "maxCrawledPlacesPerSearch": int(max_items),
            "language": "es",
            # AHORRO:
            "maxImages": 0,             
            "scrapePosts": False,       
            "reviewsDistribution": False, 
            "maxReviews": 0,            
            "oneReviewPerUser": False
        }
    
    # 2. TikTok Hashtag Scraper
    elif "tiktok" in actor_id:
        return {
            "hashtags": [busqueda.replace("#", "").strip()],
            "resultsPerPage": int(max_items),
            # AHORRO:
            "downloadCovers": False, 
            "downloadVideo": False,
            "downloadAudio": False
        }
    
    # 3. Instagram Scraper
    elif "instagram" in actor_id:
        return {
            "search": busqueda,
            "searchType": "hashtag",
            "resultsLimit": int(max_items),
            "resultsType": "details", # Clave para no bajar fotos
            # AHORRO:
            "searchLimit": 1, 
        }
        
    else:
        return {"searchQueries": [busqueda], "maxItems": int(max_items)}

# --- LÓGICA DE NORMALIZACIÓN (OUTPUTS) ---

def normalizar_datos(item, plataforma, bot_id):
    """
    Convierte el JSON sucio de Apify en el formato limpio de nuestra tabla 'prospects'.
    """
    datos = {
        "business_name": None,
        "website_url": None,
        "phone_number": None,
        "social_profiles": {},
        "address": None,
        "source_bot_id": bot_id,
        "raw_data": item # Guardamos todo por si acaso
    }

    try:
        if plataforma == "Google Maps":
            datos["business_name"] = item.get("title", item.get("name"))
            datos["website_url"] = item.get("website")
            datos["phone_number"] = item.get("phone")
            datos["address"] = item.get("address")
            if item.get("socialMedia"):
                datos["social_profiles"] = item.get("socialMedia")

        elif plataforma == "TikTok":
            author = item.get("authorMeta", {})
            datos["business_name"] = author.get("nickName") or author.get("name")
            datos["website_url"] = author.get("signatureLink")
            datos["social_profiles"] = {"tiktok": f"https://www.tiktok.com/@{author.get('name')}"}

        elif plataforma == "Instagram":
            datos["business_name"] = item.get("fullName") or item.get("username")
            datos["website_url"] = item.get("externalUrl")
            datos["social_profiles"] = {"instagram": f"https://www.instagram.com/{item.get('username')}"}
    
    except Exception as e:
        logging.error(f"Error normalizando item: {e}")
    
    return datos

# --- FUNCIÓN PRINCIPAL ---

def ejecutar_caza(campana_id, prompt_busqueda, ubicacion, plataforma="Google Maps", tipo_producto="Tangible", max_resultados=10):
    logging.info(f"🚀 INICIANDO PROTOCOLO DE CAZA | Campaña: {campana_id}")

    # 1. Consultar Arsenal
    bot_info = consultar_arsenal(plataforma, tipo_producto)
    actor_id = bot_info["actor_id"]

    # 2. Ejecutar Apify
    try:
        client = ApifyClient(APIFY_TOKEN)
        run_input = preparar_input_blindado(actor_id, prompt_busqueda, ubicacion, max_resultados)
        
        logging.info(f"📡 Llamando a Apify ({actor_id})...")
        run = client.actor(actor_id).call(run_input=run_input)
        
        if not run or run.get('status') != 'SUCCEEDED':
            logging.error("❌ La ejecución en Apify falló.")
            return False

        dataset_id = run["defaultDatasetId"]
        logging.info(f"✅ Caza completada. Descargando Dataset: {dataset_id}")

        # 3. Guardar en Base de Datos (CORREGIDO: Nombres en Inglés)
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        contador_nuevos = 0
        dataset_items = client.dataset(dataset_id).iterate_items()
        
        for item in dataset_items:
            datos = normalizar_datos(item, plataforma, actor_id)
            
            if not datos["business_name"]: continue

            try:
                # INSERTAR EN LA NUEVA TABLA 'PROSPECTS'
                cur.execute(
                    """
                    INSERT INTO prospects 
                    (campaign_id, business_name, website_url, phone_number, social_profiles, source_bot_id, status, raw_data, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, 'cazado', %s, NOW())
                    ON CONFLICT DO NOTHING 
                    RETURNING id;
                    """,
                    (
                        campana_id,
                        datos["business_name"],
                        datos["website_url"],
                        datos["phone_number"],
                        Json(datos["social_profiles"]),
                        actor_id,
                        Json(datos["raw_data"])
                    )
                )
                
                if cur.rowcount > 0:
                    contador_nuevos += 1
                    
            except Exception as db_err:
                conn.rollback()
                continue
            else:
                conn.commit()

        cur.close()
        conn.close()
        
        logging.info(f"🎉 CICLO COMPLETADO. Nuevos prospectos: {contador_nuevos}")
        return True

    except Exception as e:
        logging.critical(f"🔥 Error Catastrófico en worker_cazador: {e}")
        return False
