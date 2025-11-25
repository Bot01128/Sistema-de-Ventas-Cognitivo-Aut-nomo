import os
import json
import logging
import time
import requests
import psycopg2
from psycopg2.extras import Json
from datetime import datetime
from bs4 import BeautifulSoup
from apify_client import ApifyClient
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIGURACIÓN DE ENTORNO ---
load_dotenv()

# Configuración de Logs
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - ANALISTA - %(levelname)s - %(message)s'
)

# Credenciales
APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Configuración de IA (Cerebro del Analista)
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    modelo_ia = genai.GenerativeModel('gemini-1.5-flash') # Modelo rápido y eficiente
else:
    logging.warning("⚠️ GOOGLE_API_KEY no encontrada. El cerebro del analista estará limitado.")
    modelo_ia = None

class TrabajadorAnalista:
    def __init__(self):
        self.apify = ApifyClient(APIFY_TOKEN)

    def conectar_db(self):
        return psycopg2.connect(DATABASE_URL)

    # --- MÓDULO 1: ANÁLISIS SITIO WEB (BAJO COSTO) ---
    def analizar_web(self, url):
        """
        Escanea el HTML de la web buscando:
        1. Si la web existe.
        2. Enlaces de WhatsApp o Email.
        """
        dolores = []
        datos_contacto = {"whatsapp": None, "email": None}
        
        if not url:
            return ["SIN_SITIO_WEB"], datos_contacto

        logging.info(f"🔍 Analizando Sitio Web: {url}")
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Compatible; AutoNeuraBot/1.0)'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code >= 400:
                return ["SITIO_WEB_ROTO_ERROR_404"], datos_contacto

            soup = BeautifulSoup(response.content, 'html.parser')

            # A. Búsqueda de WhatsApp
            wa_link = soup.find("a", href=lambda h: h and ("wa.me" in h or "api.whatsapp.com" in h))
            if wa_link:
                datos_contacto["whatsapp"] = wa_link['href']
            else:
                dolores.append("SIN_ENLACE_WHATSAPP_DIRECTO")

            # B. Búsqueda de Email
            mail_link = soup.find("a", href=lambda h: h and "mailto:" in h)
            if mail_link:
                datos_contacto["email"] = mail_link['href'].replace("mailto:", "")
            
            # C. Análisis Semántico Simple
            texto_web = soup.get_text().lower()
            if "solicitar cotización" in texto_web or "llame para consultar precio" in texto_web:
                dolores.append("PRECIO_OCULTO_COMPRA_COMPLEJA")

        except Exception as e:
            logging.warning(f"⚠️ Web caída o inaccesible ({url}): {e}")
            return ["SITIO_WEB_INACCESIBLE"], datos_contacto

        return dolores, datos_contacto

    # --- MÓDULO 2: ANÁLISIS REDES SOCIALES ---
    def analizar_redes(self, perfiles_sociales):
        dolores = []
        if not perfiles_sociales:
            return ["PRESENCIA_DIGITAL_NULA"]
        return dolores

    # --- MÓDULO 3: ANÁLISIS REPUTACIÓN CON IA ---
    def analizar_reputacion_ia(self, nombre_negocio, reseñas_texto):
        if not modelo_ia or not reseñas_texto:
            return []

        dolores = []
        try:
            prompt = f"""
            Analiza estas reseñas negativas de '{nombre_negocio}': "{reseñas_texto}"
            Identifica la causa raíz: [ATENCION_LENTA, PRECIOS_ALTOS, MALA_CALIDAD].
            Responde SOLO con la categoría.
            """
            respuesta = modelo_ia.generate_content(prompt)
            categoria = respuesta.text.strip().upper().replace(" ", "_")
            dolores.append(f"PAIN_POINT_{categoria}")
            
        except Exception as e:
            logging.error(f"Error consultando a Gemini: {e}")
        
        return dolores

    # --- ORQUESTACIÓN PRINCIPAL ---
    def procesar_lote_prospectos(self, limite=5):
        """
        Toma prospectos 'cazados', analiza y guarda resultados.
        """
        conn = self.conectar_db()
        cur = conn.cursor()

        try:
            # CORRECCIÓN: Usamos 'status' y 'raw_data' (Inglés)
            cur.execute("""
                SELECT id, business_name, website_url, social_profiles, raw_data
                FROM prospects 
                WHERE status = 'cazado' 
                LIMIT %s 
                FOR UPDATE SKIP LOCKED
            """, (limite,))
            
            lote = cur.fetchall()

            if not lote:
                logging.info("💤 Nada que analizar.")
                return

            logging.info(f"🚀 Analizando {len(lote)} prospectos...")

            for prospecto in lote:
                pid, nombre, web, sociales, datos_extra = prospecto
                
                # CORRECCIÓN: 'status'
                cur.execute("UPDATE prospects SET status = 'en_analisis' WHERE id = %s", (pid,))
                conn.commit()

                puntos_dolor = []
                inteligencia_extra = {}

                # A. Análisis Web
                dolores_web, contactos_web = self.analizar_web(web)
                puntos_dolor.extend(dolores_web)
                
                if contactos_web["whatsapp"]:
                    cur.execute("UPDATE prospects SET phone_number = COALESCE(phone_number, %s) WHERE id = %s", (contactos_web["whatsapp"], pid))

                # B. Análisis Redes
                if isinstance(sociales, str): sociales = json.loads(sociales)
                dolores_redes = self.analizar_redes(sociales)
                puntos_dolor.extend(dolores_redes)

                # C. Análisis IA (Usando raw_data del cazador)
                # El campo 'datos_extra' aquí es el 'raw_data' de la DB
                if datos_extra and 'reviews' in datos_extra:
                    dolores_ia = self.analizar_reputacion_ia(nombre, datos_extra['reviews'])
                    puntos_dolor.extend(dolores_ia)

                nuevo_estado = 'analizado_exitoso'
                if not web and not sociales:
                    nuevo_estado = 'analizado_baja_calidad'

                informe_analisis = {
                    "fecha": datetime.now().isoformat(),
                    "dolores_detectados": puntos_dolor,
                    "inteligencia_extra": inteligencia_extra,
                    "score_calidad": 100 - (len(puntos_dolor) * 10)
                }

                logging.info(f"💾 Guardando análisis para ID {pid}. Estado: {nuevo_estado}")
                
                # CORRECCIÓN: 'status' y 'pain_points'
                cur.execute("""
                    UPDATE prospects 
                    SET status = %s, 
                        pain_points = %s 
                    WHERE id = %s
                """, (nuevo_estado, Json(informe_analisis), pid))
                
                conn.commit()
                time.sleep(1)

        except Exception as e:
            logging.critical(f"❌ Error catastrófico en el proceso de análisis: {e}")
            if conn: conn.rollback()
        finally:
            cur.close()
            conn.close()

# --- ENTRY POINT ---
if __name__ == "__main__":
    analista = TrabajadorAnalista()
    analista.procesar_lote_prospectos()
