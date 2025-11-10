import os
import json
from apify_client import ApifyClient
import psycopg2
from dotenv import load_dotenv

# --- CONFIGURACIÓN ---
# Carga las variables de entorno desde un archivo .env (útil para pruebas locales)
load_dotenv()

APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")

# --- CONEXIÓN AL ARSENAL (EN SUPABASE) ---
def obtener_info_herramienta(nombre_herramienta):
    """
    Busca una herramienta en la tabla arsenal_herramientas de Supabase 
    y devuelve su información.
    """
    print(f"Buscando herramienta '{nombre_herramienta}' en el Arsenal de Supabase...")
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM arsenal_herramientas WHERE nombre_herramienta = %s", (nombre_herramienta,))
        
        colnames = [desc[0] for desc in cur.description]
        fila = cur.fetchone()
        
        cur.close()
        conn.close()

        if fila:
            info = dict(zip(colnames, fila))
            print(f"Herramienta encontrada: {info.get('id_actor')}")
            return info
        else:
            print(f"!!! ERROR: Herramienta '{nombre_herramienta}' no encontrada en el Arsenal.")
            return None

    except Exception as e:
        print(f"!!! ERROR al leer el Arsenal de Supabase: {e} !!!")
        if conn:
            conn.close()
        return None

# --- FUNCIÓN PRINCIPAL DE CAZA ---
def cazar_prospectos(campana_id, herramienta, busqueda, ubicacion, max_resultados):
    print(f"\n--- Iniciando la caza para la Campaña ID: {campana_id} ---")
    
    info_herramienta = obtener_info_herramienta(herramienta)
    
    if not info_herramienta:
        return

    id_actor = info_herramienta.get('id_actor')
    if not id_actor:
        print("!!! ERROR: El 'id_actor' no está definido para esta herramienta en el Arsenal.")
        return

    try:
        apify_client = ApifyClient(APIFY_TOKEN)
        
        run_input = {
            "searchStringsArray": [busqueda],
            "locationQuery": ubicacion,
            "maxCrawledPlacesPerSearch": max_resultados,
        }
        
        print(f"Usando el Actor '{id_actor}' para buscar '{busqueda}' en '{ubicacion}'...")
        run = apify_client.actor(id_actor).call(run_input=run_input)
        
        print("--- Caza en Apify completada. Procesando y guardando resultados... ---")

        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        prospectos_guardados = 0
        for item in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
            nombre = item.get("title")
            telefono = item.get("phone")
            web = item.get("website")
            url_gmaps = item.get("url")

            cur.execute(
                """
                INSERT INTO prospectos 
                (nombre_negocio, telefono, sitio_web, url_gmaps, estado_prospecto, campana_id) 
                VALUES (%s, %s, %s, %s, %s, %s) 
                ON CONFLICT (url_gmaps) DO NOTHING
                """,
                (nombre, telefono, web, url_gmaps, 'cazado', campana_id)
            )
            
            if cur.rowcount > 0:
                prospectos_guardados += 1

        conn.commit()
        cur.close()
        conn.close()
        
        print(f"\n--- ¡VICTORIA! ---")
        print(f"Se han guardado {prospectos_guardados} nuevos prospectos para la campaña {campana_id}.")

    except Exception as e:
        print(f"!!! Ocurrió un error catastrófico durante la caza: {e} !!!")

# --- EJECUCIÓN DE PRUEBA DEL SCRIPT ---
if __name__ == "__main__":
    # La orden que vendría del "Orquestador" en el futuro
    id_de_campana_prueba = 1
    herramienta_a_usar = "Cazador Principal Gmaps"
    tipo_negocio = "ferreterías"
    ciudad_pais = "Caracas, Venezuela"
    cantidad = 5

    cazar_prospectos(id_de_campana_prueba, herramienta_a_usar, tipo_negocio, ciudad_pais, cantidad)
