import os
import json
from apify_client import ApifyClient
import psycopg2
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN ---
load_dotenv()

APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_SHEETS_CREDENTIALS_JSON = os.environ.get("GOOGLE_SHEETS_CREDENTIALS")

# --- CONEXIÓN AL ARSENAL (GOOGLE SHEETS) ---
def obtener_info_herramienta(nombre_herramienta):
    print(f"Buscando herramienta '{nombre_herramienta}' en el Arsenal...")
    try:
        creds_dict = json.loads(GOOGLE_SHEETS_CREDENTIALS_JSON)
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        sheet = client.open("Arsenal_AutoNeura").sheet1
        
        # Buscar la fila que coincide con el nombre de la herramienta
        lista_de_listas = sheet.get_all_values()
        encabezados = lista_de_listas[0]
        for fila in lista_de_listas[1:]:
            if fila[0] == nombre_herramienta:
                info = dict(zip(encabezados, fila))
                print(f"Herramienta encontrada: {info['ID_Actor']}")
                return info
        return None
    except Exception as e:
        print(f"!!! ERROR al leer el Arsenal de Google Sheets: {e} !!!")
        return None

# --- FUNCIÓN PRINCIPAL DE CAZA ---
def cazar_prospectos(herramienta, busqueda, ubicacion, max_resultados):
    print("--- Iniciando la caza ---")
    
    info_herramienta = obtener_info_herramienta(herramienta)
    
    if not info_herramienta:
        print(f"!!! ERROR: No se encontró la herramienta '{herramienta}' en el Arsenal.")
        return

    id_actor = info_herramienta.get('ID_Actor')
    if not id_actor:
        print("!!! ERROR: El ID_Actor no está definido para esta herramienta en el Arsenal.")
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
        
        print("--- Caza en Apify completada. Procesando resultados... ---")

        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        prospectos_guardados = 0
        for item in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
            nombre = item.get("title")
            telefono = item.get("phone")
            web = item.get("website")
            url_gmaps = item.get("url")

            cur.execute(
                "INSERT INTO prospectos (nombre_negocio, telefono, sitio_web, url_gmaps, estado) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (url_gmaps) DO NOTHING",
                (nombre, telefono, web, url_gmaps, 'cazado')
            )
            
            if cur.rowcount > 0:
                prospectos_guardados += 1

        conn.commit()
        cur.close()
        conn.close()
        
        print(f"\n--- ¡VICTORIA! ---")
        print(f"Se han guardado {prospectos_guardados} nuevos prospectos en la base de datos.")

    except Exception as e:
        print(f"!!! Ocurrió un error catastrófico: {e} !!!")

# --- EJECUCIÓN DEL SCRIPT ---
if __name__ == "__main__":
    # La orden que vendría del "Orquestador" en el futuro
    herramienta_a_usar = "Cazador Google Maps"
    tipo_negocio = "talleres mecánicos"
    ciudad_pais = "Bogotá, Colombia"
    cantidad = 10 # Cazar 10 para probar

    cazar_prospectos(herramienta_a_usar, tipo_negocio, ciudad_pais, cantidad)
