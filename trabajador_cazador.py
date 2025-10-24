import os
from apify_client import ApifyClient
import psycopg2
from dotenv import load_dotenv

# --- CONFIGURACIÓN ---
# Carga las variables de entorno desde los "Secrets" de Replit
load_dotenv()

APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")

# --- FUNCIÓN PRINCIPAL DE CAZA ---
def cazar_en_google_maps(busqueda, ubicacion, max_resultados):
    print("--- Iniciando la caza en Google Maps ---")
    
    if not APIFY_TOKEN or not DATABASE_URL:
        print("!!! ERROR: Asegúrate de que APIFY_API_TOKEN y DATABASE_URL están en los Secrets.")
        return

    try:
        # 1. Conectar con Apify
        apify_client = ApifyClient(APIFY_TOKEN)
        
        # 2. Preparar la orden para el "Actor" de Google Maps
        run_input = {
            "searchStringsArray": [busqueda],
            "locationQuery": ubicacion,
            "maxCrawledPlacesPerSearch": max_resultados,
        }
        
        print(f"Buscando '{busqueda}' en '{ubicacion}' (máx {max_resultados} resultados)...")

        # 3. Ejecutar el "Actor" y esperar los resultados
        run = apify_client.actor("apify/google-maps-scraper").call(run_input=run_input)
        
        print("--- Caza en Apify completada. Procesando resultados... ---")

        # 4. Conectar con la Base de Datos
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # 5. Iterar y guardar los prospectos
        prospectos_guardados = 0
        for item in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
            nombre = item.get("title")
            telefono = item.get("phone")
            web = item.get("website")
            url_gmaps = item.get("url")

            # Evitar duplicados usando la URL de Google Maps que es única
            cur.execute(
                "INSERT INTO prospectos (nombre_negocio, telefono, sitio_web, url_gmaps, estado) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (url_gmaps) DO NOTHING",
                (nombre, telefono, web, url_gmaps, 'cazado')
            )
            
            if cur.rowcount > 0: # rowcount > 0 significa que se insertó una fila nueva
                prospectos_guardados += 1

        # 6. Confirmar cambios y cerrar conexiones
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"\n--- ¡VICTORIA! ---")
        print(f"Se han guardado {prospectos_guardados} nuevos prospectos en la base de datos.")

    except Exception as e:
        print(f"!!! Ocurrió un error catastrófico: {e} !!!")


# --- EJECUCIÓN DEL SCRIPT ---
if __name__ == "__main__":
    # Aquí definimos qué queremos cazar
    tipo_negocio = "restaurantes"
    ciudad_pais = "Miami, Florida"
    cantidad = 5 # Empecemos con 5 para probar

    cazar_en_google_maps(tipo_negocio, ciudad_pais, cantidad)
