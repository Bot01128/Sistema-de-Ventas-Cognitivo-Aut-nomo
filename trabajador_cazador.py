import os
import json
import logging
from apify_client import ApifyClient
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

# --- CONFIGURACIÓN INICIAL ---
load_dotenv()

# Configuración de Logs (Te permitirá ver en la consola de Railway qué está pasando)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - CAZADOR - %(levelname)s - %(message)s')

APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")

# --- LÓGICA DE INTELIGENCIA (EL ARSENAL) ---

def consultar_arsenal(plataforma_objetivo, tipo_producto, mision="Extraer negocios locales"):
    """
    Consulta la tabla 'bot_arsenal' en Supabase para obtener el mejor 'Actor'
    disponible y activo para la tarea.
    """
    logging.info(f"🔎 Consultando Arsenal para: Plataforma={plataforma_objetivo}, Producto={tipo_producto}")
    
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Mapeo para coincidir con tu base de datos (Tangible/Intangible)
        tipo_prod_db = 'Intangible' if 'intangible' in str(tipo_producto).lower() else 'Tangible'
        
        # QUERY INTELIGENTE:
        # 1. Busca coincidencia de plataforma.
        # 2. Busca coincidencia de tipo de producto O que sirva para "Ambos".
        # 3. Solo bots activos.
        # 4. Ordena por Nivel de Confianza (el mejor primero).
        query = """
            SELECT tool_name, actor_id, provider 
            FROM bot_arsenal 
            WHERE platform_target = %s 
            AND (product_type_focus = %s OR product_type_focus = 'Ambos')
            AND is_active = TRUE
            ORDER BY confidence_level DESC
            LIMIT 1;
        """
        
        cur.execute(query, (plataforma_objetivo, tipo_prod_db))
        resultado = cur.fetchone()
        
        cur.close()
        
        if resultado:
            logging.info(f"✅ Bot Seleccionado: {resultado[0]} (ID: {resultado[1]}) - Proveedor: {resultado[2]}")
            return {"nombre": resultado[0], "actor_id": resultado[1], "provider": resultado[2]}
        else:
            logging.warning("⚠️ No se encontró ningún bot adecuado en el Arsenal. Verifica tu tabla 'bot_arsenal'.")
            return None

    except Exception as e:
        logging.error(f"❌ Error conectando al Arsenal: {e}")
        return None
    finally:
        if conn: conn.close()

# --- LÓGICA DE AHORRO Y EJECUCIÓN (INPUTS) ---

def preparar_input_blindado(actor_id, busqueda, ubicacion, max_items):
    """
    Configura los parámetros del Bot asegurando el AHORRO DE COSTOS.
    Desactiva imágenes y videos.
    """
    logging.info(f"⚙️ Configurando parámetros de ahorro para: {actor_id}")

    # 1. Google Maps (Compass o Apify Oficial)
    if "google-maps" in actor_id or "google-places" in actor_id:
        return {
            "searchStringsArray": [busqueda],
            "locationQuery": ubicacion,
            "maxCrawledPlacesPerSearch": int(max_items),
            "language": "es",
            # --- MEDIDAS DE AHORRO EXTREMO ---
            "maxImages": 0,             # NO descargar imágenes
            "scrapePosts": False,       # NO descargar posts
            "reviewsDistribution": False, # NO analizar reviews a fondo
            "reviewsSort": "newest",
            "maxReviews": 0,            # Solo queremos datos de contacto, no reviews
            "oneReviewPerUser": False,
            "allPlacesNoSearchAction": False 
        }
    
    # 2. TikTok Hashtag Scraper
    elif "tiktok-hashtag" in actor_id:
        hashtag = busqueda.replace("#", "").strip()
        return {
            "hashtags": [hashtag],
            "resultsPerPage": int(max_items),
            # --- MEDIDAS DE AHORRO ---
            "shouldDownloadCovers": False, 
            "shouldDownloadSlideshowImages": False,
            "shouldDownloadVideo": False,
            "shouldDownloadAuthorAvatar": False
        }
    
    # 3. Instagram Scraper
    elif "instagram-scraper" in actor_id:
        return {
            "search": busqueda,
            "searchType": "hashtag",
            "resultsLimit": int(max_items),
            # --- MEDIDAS DE AHORRO ---
            "searchLimit": 1, # Limitar búsquedas profundas
        }
        
    # Configuración Genérica (Fallback)
    else:
        return {
            "searchQueries": [busqueda],
            "maxItems": int(max_items)
        }

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
        "raw_data": {} # Opcional: guardar un resumen
    }

    try:
        if plataforma == "Google Maps":
            datos["business_name"] = item.get("title")
            datos["website_url"] = item.get("website")
            datos["phone_number"] = item.get("phone")
            datos["address"] = item.get("address")
            
            # Intentar extraer redes sociales si el bot las encontró
            if item.get("socialMedia"):
                datos["social_profiles"] = item.get("socialMedia")
            
            # Fallback para nombre si está vacío
            if not datos["business_name"]:
                datos["business_name"] = item.get("name")

        elif plataforma == "TikTok":
            author = item.get("authorMeta", {})
            datos["business_name"] = author.get("nickName") or author.get("name") or item.get("text")
            datos["website_url"] = author.get("signatureLink")
            datos["social_profiles"] = {"tiktok": f"https://www.tiktok.com/@{author.get('name')}"}
            datos["raw_data"] = {"diggCount": item.get("diggCount"), "playCount": item.get("playCount")}

        elif plataforma == "Instagram":
            datos["business_name"] = item.get("fullName") or item.get("username")
            datos["website_url"] = item.get("externalUrl")
            datos["social_profiles"] = {"instagram": f"https://www.instagram.com/{item.get('username')}"}
    
    except Exception as e:
        logging.error(f"Error normalizando item: {e}")
    
    return datos

# --- FUNCIÓN PRINCIPAL (LA QUE LLAMA EL ORQUESTADOR) ---

def ejecutar_caza(campana_id, prompt_busqueda, ubicacion, plataforma="Google Maps", tipo_producto="Tangible", max_resultados=10):
    """
    Función maestra ejecutada por el Orquestador.
    1. Consulta Arsenal.
    2. Configura Apify (con ahorro).
    3. Ejecuta Caza.
    4. Guarda en Supabase.
    """
    logging.info(f"🚀 INICIANDO PROTOCOLO DE CAZA | Campaña: {campana_id}")

    # 1. Consultar Arsenal
    bot_info = consultar_arsenal(plataforma, tipo_producto)
    if not bot_info:
        logging.error("⛔ Abortando caza: No hay bot disponible.")
        return False

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
        logging.info(f"✅ Caza en Apify completada. Descargando Dataset: {dataset_id}")

        # 3. Guardar en Base de Datos (Supabase)
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        contador_nuevos = 0
        dataset_items = client.dataset(dataset_id).iterate_items()
        
        for item in dataset_items:
            # Normalizar
            datos = normalizar_datos(item, plataforma, actor_id)
            
            # Filtro básico: Si no hay nombre, no nos sirve
            if not datos["business_name"]:
                continue

            # Insertar (Usando los nombres de columna de tu FOTO de Supabase)
            try:
                # Nota: 'campana_id' en la tabla se llama 'campaign_id' según tu esquema visualizado, 
                # ajusta el SQL abajo si en tu DB es 'campana_id'
                cur.execute(
                    """
                    INSERT INTO prospects 
                    (campana_id, business_name, website_url, phone_number, social_profiles, source_bot_id, estado_prospecto, datos_json, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, 'cazado', %s, NOW())
                    ON CONFLICT (website_url) DO NOTHING 
                    RETURNING id;
                    """,
                    (
                        campana_id,
                        datos["business_name"],
                        datos["website_url"],
                        datos["phone_number"],
                        Json(datos["social_profiles"]),
                        actor_id,
                        Json(datos["raw_data"]) # datos_json extra
                    )
                )
                # Nota sobre ON CONFLICT: Idealmente deberías tener un constraint unique en website_url o business_name+phone
                # Si no tienes constraint, quita la línea "ON CONFLICT..."
                
                if cur.rowcount > 0:
                    contador_nuevos += 1
            except Exception as db_err:
                # Si falla una inserción (ej: duplicado sin constraint), lo ignoramos y seguimos
                conn.rollback()
                logging.debug(f"Salto de fila (posible duplicado o error): {db_err}")
                continue
            else:
                conn.commit() # Commit por éxito individual (o por lote si prefieres velocidad)

        cur.close()
        conn.close()
        
        logging.info(f"🎉 CICLO COMPLETADO. Nuevos prospectos guardados: {contador_nuevos}")
        return True

    except Exception as e:
        logging.critical(f"🔥 Error Catastrófico en worker_cazador: {e}")
        return False

# --- BLOQUE DE PRUEBA (SOLO SE EJECUTA SI CORRES ESTE ARCHIVO DIRECTAMENTE) ---
if __name__ == "__main__":
    print(">> Modo de Prueba Manual del Trabajador Cazador")
    # Para probar, descomenta y pon un ID de campaña real de tu tabla 'campanas'
    # ejecutar_caza(
    #     campana_id=1, 
    #     prompt_busqueda="Ferreterias industriales", 
    #     ubicacion="Bogota, Colombia", 
    #     plataforma="Google Maps", 
    #     tipo_producto="Tangible", 
    #     max_resultados=5
    # )
