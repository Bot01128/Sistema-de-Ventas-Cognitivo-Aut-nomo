import os
import json
import requests
from bs4 import BeautifulSoup
import psycopg2
from dotenv import load_dotenv
import re

# --- CONFIGURACIÓN ---
load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

# --- FUNCIÓN DE ANÁLISIS WEB ---
def analizar_sitio_web(url):
    print(f"Analizando sitio web: {url}...")
    informe = {
        "whatsapp_encontrado": None,
        "email_encontrado": None,
        "chat_widget_presente": False
    }

    try:
        # Intentamos descargar la página con un tiempo de espera de 10 segundos
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Buscar WhatsApp
            # Buscamos enlaces que contengan 'wa.me' o 'api.whatsapp.com'
            whatsapp_links = soup.find_all('a', href=re.compile(r'wa\.me|api\.whatsapp\.com'))
            if whatsapp_links:
                # Extraemos el primer enlace encontrado como ejemplo
                informe["whatsapp_encontrado"] = whatsapp_links[0]['href']

            # 2. Buscar Email
            # Buscamos enlaces 'mailto:'
            email_links = soup.find_all('a', href=re.compile(r'^mailto:'))
            if email_links:
                # Extraemos el email quitando el 'mailto:'
                informe["email_encontrado"] = email_links[0]['href'].replace('mailto:', '')

            # 3. Buscar Widgets de Chat Comunes
            # Buscamos scripts conocidos en el código HTML
            html_text = response.text.lower()
            if 'tawk.to' in html_text or 'intercom' in html_text or 'zendesk' in html_text or 'tidio' in html_text:
                informe["chat_widget_presente"] = True

        else:
             print(f"!!! ERROR: No se pudo acceder al sitio. Código de estado: {response.status_code}")
             informe["error_acceso"] = f"Status code: {response.status_code}"

    except Exception as e:
        print(f"!!! ERROR al analizar el sitio web: {e}")
        informe["error_acceso"] = str(e)

    return informe

# --- FUNCIÓN PRINCIPAL DEL TRABAJADOR ---
def ejecutar_analisis():
    print("--- Trabajador Analista v1.0 INICIADO ---")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # 1. Buscar un prospecto para analizar (que esté 'cazado' y tenga sitio web)
        # Usamos 'FOR UPDATE SKIP LOCKED' para que si ejecutamos varios analistas a la vez, no tomen el mismo prospecto.
        cur.execute("""
            SELECT id, nombre_negocio, sitio_web 
            FROM prospectos 
            WHERE estado = 'cazado' AND sitio_web IS NOT NULL
            LIMIT 1
            FOR UPDATE SKIP LOCKED
        """)
        
        prospecto = cur.fetchone()

        if prospecto:
            prospecto_id, nombre, url_web = prospecto
            print(f">>> Prospecto encontrado para análisis: {nombre} (ID: {prospecto_id})")

            # 2. Realizar el análisis
            informe_json = analizar_sitio_web(url_web)

            # 3. Guardar los resultados
            cur.execute("""
                UPDATE prospectos 
                SET estado = %s, informe_analisis = %s
                WHERE id = %s
            """, ('analizado_exitoso', json.dumps(informe_json), prospecto_id))
            
            conn.commit()
            print(f"--- ¡ANÁLISIS COMPLETADO Y GUARDADO! ---")
            print(f"Informe generado: {json.dumps(informe_json, indent=2)}")

        else:
            print("--- No hay prospectos 'cazados' con sitio web esperando análisis. ---")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"!!! Ocurrió un error catastrófico en el Analista: {e} !!!")

# --- EJECUCIÓN ---
if __name__ == "__main__":
    ejecutar_analisis()
