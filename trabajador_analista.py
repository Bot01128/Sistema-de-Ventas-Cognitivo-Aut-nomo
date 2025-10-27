import os
import json
from apify_client import ApifyClient
import psycopg2
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# --- CONFIGURACIÓN ---
load_dotenv()

APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Configurar la IA de Google
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print(">>> IA de Google configurada exitosamente.")
else:
    print("!!! ADVERTENCIA: GOOGLE_API_KEY no encontrada. El análisis de IA estará desactivado.")

# --- FUNCIÓN DE ANÁLISIS CON IA ---
def analizar_resenas_con_ia(resenas):
    if not GOOGLE_API_KEY or not resenas:
        return "N/A"
    
    print(f"--- Analizando {len(resenas)} reseñas con IA... ---")
    
    # Juntamos solo el texto de las reseñas negativas
    texto_resenas = "\n".join([r.get('text', '') for r in resenas if r.get('stars', 5) <= 3 and r.get('text')])
    
    if not texto_resenas:
        print("--- No se encontraron reseñas negativas con texto para analizar. ---")
        return "Sin quejas relevantes"

    prompt = f"""
    Eres un analista de reputación de negocios. Lee las siguientes reseñas negativas de un negocio. 
    Tu única tarea es identificar la queja principal y recurrente y resumirla en UNA de estas categorías: 
    [Mal Servicio/Atención, Precios Altos, Mala Calidad del Producto, Problemas con Tiempos/Reservas, Otro].
    No añadas explicaciones. Solo devuelve la categoría.

    RESEÑAS:
    {texto_resenas}

    CATEGORÍA:
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        categoria = response.text.strip()
        print(f">>> IA ha categorizado la queja principal como: {categoria}")
        return categoria
    except Exception as e:
        print(f"!!! ERROR durante el análisis de IA: {e}")
        return "Error de IA"

# --- FUNCIÓN PRINCIPAL DEL ANALISTA ---
def analizar_prospecto():
    print("\n--- Trabajador Analista v1.1 INICIADO ---")
    
    conn = None
    try:
        # 1. Conectar a la DB y buscar un prospecto
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Buscamos un prospecto cazado que no haya sido analizado aún
        cur.execute("SELECT id, nombre_negocio, sitio_web, url_gmaps FROM prospectos WHERE estado = 'cazado' LIMIT 1")
        prospecto = cur.fetchone()
        
        if not prospecto:
            print(">>> No se encontraron nuevos prospectos para analizar. Misión cumplida.")
            return

        prospecto_id, nombre, web, url_gmaps = prospecto
        print(f">>> Prospecto encontrado para análisis: {nombre} (ID: {prospecto_id})")
        
        # Cambiamos el estado para que otro analista no lo tome
        cur.execute("UPDATE prospectos SET estado = 'en_analisis' WHERE id = %s", (prospecto_id,))
        conn.commit()

        informe = {
            "puntos_de_dolor": [],
            "inteligencia_adicional": {}
        }

        # 2. Analizar el sitio web (si existe)
        if web:
            print(f"Analizando sitio web: {web}...")
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                response = requests.get(web, headers=headers, timeout=15)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                if not soup.find("a", href=lambda href: href and "wa.me" in href):
                    informe["puntos_de_dolor"].append("SIN_WHATSAPP_WEB")
                
                if not soup.find("a", href=lambda href: href and "mailto:" in href):
                     informe["puntos_de_dolor"].append("SIN_EMAIL_VISIBLE")

            except Exception as e:
                print(f"!!! ERROR al analizar el sitio web: {e}")
                informe["error_web"] = str(e)

        # 3. Analizar las reseñas de Google Maps con Apify e IA
        if url_gmaps:
            print(f"Extrayendo reseñas de Google Maps: {url_gmaps}...")
            try:
                apify_client = ApifyClient(APIFY_TOKEN)
                run_input = { "startUrls": [{ "url": url_gmaps }], "maxReviews": 20 }
                run = apify_client.actor("compass/crawler-google-places").call(run_input=run_input)
                
                resenas = list(apify_client.dataset(run["defaultDatasetId"]).iterate_items())
                
                # Llamamos a nuestra nueva función de IA
                queja_principal = analizar_resenas_con_ia(resenas)
                informe["inteligencia_adicional"]["queja_principal_resenas"] = queja_principal
                if queja_principal not in ["N/A", "Sin quejas relevantes", "Error de IA"]:
                    informe["puntos_de_dolor"].append(f"RESEÑAS_NEGATIVAS_{queja_principal.upper().replace(' ', '_')}")

            except Exception as e:
                print(f"!!! ERROR al extraer reseñas: {e}")
                informe["error_resenas"] = str(e)

        # 4. Guardar el informe final en la base de datos
        print("--- ¡ANÁLISIS COMPLETADO! Guardando informe... ---")
        print(json.dumps(informe, indent=2))
        
        cur.execute(
            "UPDATE prospectos SET estado = %s, informe_analisis = %s WHERE id = %s",
            ('analizado_exitoso', json.dumps(informe), prospecto_id)
        )
        conn.commit()
        print(">>> Informe guardado en la base de datos.")

    except Exception as e:
        print(f"!!! Ocurrió un error catastrófico en el Analista: {e} !!!")
        # Si algo falla, revertimos el estado para que pueda ser reintentado
        if conn and prospecto_id:
            cur.execute("UPDATE prospectos SET estado = 'cazado_con_error' WHERE id = %s", (prospecto_id,))
            conn.commit()

    finally:
        if conn:
            cur.close()
            conn.close()

# --- EJECUCIÓN DEL SCRIPT ---
if __name__ == "__main__":
    analizar_prospecto()
