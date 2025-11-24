import os
import json
import logging
from apify_client import ApifyClient
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

# --- CONFIGURACIÓN INICIAL ---
load_dotenv()

# Configuración de Logs para depuración profesional
logging.basicConfig(level=logging.INFO, format='%(asctime)s - CAZADOR - %(levelname)s - %(message)s')

APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")

# --- LÓGICA DE CEREBRO (ARSENAL) ---

def obtener_mejor_bot(plataforma_objetivo, tipo_producto, mision="Extraer negocios locales"):
    """
    Consulta la tabla 'bot_arsenal' en Supabase para encontrar el mejor Bot (Actor)
    disponible basado en la estrategia de la campaña.
    """
    logging.info(f"Consultando Arsenal para: Plataforma={plataforma_objetivo}, Producto={tipo_producto}")
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Selecciona el bot con mayor nivel de confianza que coincida con los criterios
        query = """
            SELECT tool_name, actor_id, provider 
            FROM bot_arsenal 
            WHERE platform_target = %s 
            AND (product_type_focus = %s OR product_type_focus = 'Ambos')
            AND is_active = TRUE
            ORDER BY confidence_level DESC
            LIMIT 1;
        """
        # Mapeo simple para asegurar que coincida con los valores de la DB
        tipo_prod_db = 'Intangible' if 'intangible' in tipo_producto.lower() else 'Tangible'
        
        cur.execute(query, (plataforma_objetivo, tipo_prod_db))
        resultado = cur.fetchone()
        
        cur.close()
        conn.close()

        if resultado:
            logging.info(f"Bot Seleccionado: {resultado[0]} (ID: {resultado[1]})")
            return {"nombre": resultado[0], "actor_id": resultado[1], "provider": resultado[2]}
        else:
            logging.error("No se encontró ningún bot adecuado en el Arsenal.")
            return None

    except Exception as e:
        logging.error(f"Error crítico conectando al Arsenal: {e}")
        if conn: conn.close()
        return None

# --- LÓGICA DE ADAPTACIÓN (INPUTS) ---

def preparar_input_actor(actor_id, busqueda, ubicacion, max_items):
    """
    Adapta los parámetros de búsqueda al formato JSON específico que requiere cada Bot.
    """
    # 1. Configuración para Google Maps Scraper (Compass o Apify oficial)
    if "google-maps" in actor_id or "google-places" in actor_id:
        return {
            "searchStringsArray": [busqueda],
            "locationQuery": ubicacion,
            "maxCrawledPlacesPerSearch": max_items,
            "language": "es", # Se puede parametrizar según campaña
            "allPlacesNoSearchAction": False
        }
    
    # 2. Configuración para TikTok Hashtag Scraper
    elif "tiktok-hashtag" in actor_id:
        # Asumimos que 'busqueda' es el hashtag
        hashtag = busqueda.replace("#", "").strip()
        return {
            "hashtags": [hashtag],
            "resultsPerPage": max_items,
            "shouldDownloadCovers": False
        }
    
    # 3. Configuración para Instagram Scraper
    elif "instagram-scraper" in actor_id:
        return {
            "search": busqueda,
            "searchType": "hashtag",
            "resultsLimit": max_items
        }
        
    # Default (intento genérico)
    else:
        return {
            "searchQueries": [busqueda],
            "maxItems": max_items
        }

# --- LÓGICA DE NORMALIZACIÓN (OUTPUTS) ---

def normalizar_resultado(item, plataforma):
    """
    Toma el JSON crudo de Apify y lo convierte en un diccionario estandarizado
    para nuestra tabla 'prospects'.
    """
    datos_normalizados = {
        "business_name": None,
        "website_url": None,
        "phone_number": None,
        "social_profiles": {},
        "address": None,
        "url_fuente": None
    }

    if plataforma == "Google Maps":
        datos_normalizados["business_name"] = item.get("title")
        datos_normalizados["website_url"] = item.get("website")
        datos_normalizados["phone_number"] = item.get("phone")
        datos_normalizados["address"] = item.get("address")
        datos_normalizados["url_fuente"] = item.get("url") # URL de Gmaps
        
        # Extraer redes sociales si el scraper las detectó
        if item.get("socialMedia"):
            datos_normalizados["social_profiles"] = item.get("socialMedia")

    elif plataforma == "TikTok":
        author = item.get("authorMeta", {})
        datos_normalizados["business_name"] = author.get("nickName") or author.get("name")
        datos_normalizados["website_url"] = author.get("signatureLink") # Link en bio
        datos_normalizados["url_fuente"] = item.get("webVideoUrl")
        datos_normalizados["social_profiles"] = {"tiktok": f"https://www.tiktok.com/@{author.get('name')}"}

    elif plataforma == "Instagram":
        datos_normalizados["business_name"] = item.get("fullName") or item.get("username")
        datos_normalizados["url_fuente"] = f"https://www.instagram.com/{item.get('username')}"
        # Instagram a veces requiere más procesamiento para sacar email/web
    
    return datos_normalizados

# --- PROCESO PRINCIPAL ---

def ejecutar_caza(campana_id, prompt_busqueda, ubicacion, plataforma="Google Maps", max_resultados=10):
    """
    Función orquestada. Recibe la orden, busca la herramienta, ejecuta y guarda.
    """
    logging.info(f"--- INICIANDO PROTOCOLO DE CAZA: Campaña {campana_id} ---")
    
    # 1. Obtener detalles de la campaña (Tipo de producto, etc.) para elegir bot
    # (Aquí simplificamos asumiendo que el Orquestador nos pasa lo necesario, 
    # pero idealmente haríamos un SELECT a la tabla campaigns)
    tipo_producto_simulado = "Tangible" # Esto vendría de la DB
    
    # 2. Consultar Arsenal
    bot_info = obtener_mejor_bot(plataforma, tipo_producto_simulado)
    if not bot_info:
        return

    # 3. Ejecutar Apify
    try:
        client = ApifyClient(APIFY_TOKEN)
        actor_id = bot_info["actor_id"]
        
        run_input = preparar_input_actor(actor_id, prompt_busqueda, ubicacion, max_resultados)
        
        logging.info(f"Lanzando Actor Apify: {actor_id}")
        logging.info(f"Query: {prompt_busqueda} en {ubicacion}")
        
        run = client.actor(actor_id).call(run_input=run_input)
        
        if not run or run.get('status') != 'SUCCEEDED':
            logging.error("La ejecución del Actor en Apify falló o no terminó correctamente.")
            return

        dataset_id = run["defaultDatasetId"]
        logging.info(f"Caza finalizada. Dataset ID: {dataset_id}. Procesando resultados...")

        # 4. Guardar en Base de Datos (Supabase)
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        contador_nuevos = 0
        
        for item in client.dataset(dataset_id).iterate_items():
            # Normalizar datos
            datos = normalizar_resultado(item, plataforma)
            
            if not datos["business_name"]: continue # Saltar si no hay nombre

            # Insertar en DB (Tabla prospects)
            # Usamos ON CONFLICT DO NOTHING para evitar duplicados si ya cazamos este negocio/url
            try:
                cur.execute(
                    """
                    INSERT INTO prospects 
                    (campaign_id, business_name, website_url, phone_number, social_profiles, source_bot_id, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, (SELECT id FROM bot_arsenal WHERE actor_id = %s LIMIT 1), 'cazado', NOW())
                    ON CONFLICT DO NOTHING
                    RETURNING id;
                    """,
                    (
                        campana_id,
                        datos["business_name"],
                        datos["website_url"],
                        datos["phone_number"],
                        Json(datos["social_profiles"]),
                        actor_id
                    )
                )
                
                if cur.fetchone():
                    contador_nuevos += 1
            except Exception as db_err:
                logging.warning(f"Error guardando fila: {db_err}")
                conn.rollback() # Rollback parcial si falla una fila
                continue

        conn.commit()
        cur.close()
        conn.close()
        
        logging.info(f"--- MISIÓN CUMPLIDA ---")
        logging.info(f"Se han añadido {contador_nuevos} nuevos prospectos a la base de datos.")

    except Exception as e:
        logging.critical(f"Error Catastrófico en el proceso de caza: {e}")

# --- ENTRY POINT (SIMULACIÓN DEL ORQUESTADOR) ---
if __name__ == "__main__":
    # Esto simula la llamada que haría el Orquestador (main.py)
    
    # Datos que vendrían de la IA y la Campaña
    ID_CAMPAÑA_PRUEBA = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11" # Un UUID válido de tu tabla campaigns
    PROMPT_IA = "Clinicas dentales"
    UBICACION = "Medellin, Colombia"
    PLATAFORMA = "Google Maps" 
    
    print(">> Iniciando prueba de trabajador_cazador.py...")
    if APIFY_TOKEN and DATABASE_URL:
        ejecutar_caza(ID_CAMPAÑA_PRUEBA, PROMPT_IA, UBICACION, PLATAFORMA, max_resultados=5)
    else:
        print("Faltan variables de entorno (APIFY_TOKEN o DATABASE_URL). Revisa tu archivo .env")
