import os
import json
import logging
import requests
import psycopg2
from psycopg2.extras import Json
from datetime import datetime, timedelta
from dateutil import parser
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

# Configuración de IA
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    logging.warning("GOOGLE_API_KEY no encontrada. El cerebro del analista estará limitado.")

class TrabajadorAnalista:
    def __init__(self):
        self.apify = ApifyClient(APIFY_TOKEN)
        self.model = genai.GenerativeModel('gemini-1.5-flash') if GOOGLE_API_KEY else None

    def conectar_db(self):
        return psycopg2.connect(DATABASE_URL)

    # --- MÓDULO 1: ANÁLISIS SITIO WEB ---
    def analizar_web(self, url):
        """
        Verifica si la web funciona y busca huellas de contacto.
        Retorna: Lista de dolores encontrados y datos de contacto extraídos.
        """
        dolores = []
        datos_contacto = {"whatsapp": None, "email": None}
        
        if not url:
            return ["SIN_SITIO_WEB"], datos_contacto

        logging.info(f"🔍 Analizando Sitio Web: {url}")
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Compatible; AutoNeuraBot/1.0)'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code >= 400:
                return ["SITIO_WEB_ROTO_ERROR_404"], datos_contacto

            soup = BeautifulSoup(response.content, 'html.parser')

            # Buscar WhatsApp
            wa_link = soup.find("a", href=lambda h: h and ("wa.me" in h or "api.whatsapp.com" in h))
            if wa_link:
                datos_contacto["whatsapp"] = wa_link['href']
            else:
                dolores.append("SIN_ENLACE_WHATSAPP_DIRECTO")

            # Buscar Email
            mail_link = soup.find("a", href=lambda h: h and "mailto:" in h)
            if mail_link:
                datos_contacto["email"] = mail_link['href'].replace("mailto:", "")
            
            # Buscar palabras clave de venta difícil (e.g., "Cotizar", "Llamar para precio")
            texto_web = soup.get_text().lower()
            if "llamar para precio" in texto_web or "cotizar" in texto_web:
                dolores.append("PROCESO_COMPRA_COMPLEJO")

        except Exception as e:
            logging.warning(f"Web caída o inaccesible: {e}")
            return ["SITIO_WEB_INACCESIBLE"], datos_contacto

        return dolores, datos_contacto

    # --- MÓDULO 2: ANÁLISIS REDES SOCIALES (ACTIVIDAD Y ATENCIÓN) ---
    def analizar_redes(self, perfiles_sociales):
        """
        Analiza frecuencia de posteo y calidad de respuestas en comentarios.
        """
        dolores = []
        
        if not perfiles_sociales:
            return ["PRESENCIA_DIGITAL_NULA"]

        logging.info("📱 Analizando Redes Sociales...")

        # Ejemplo con Instagram (se puede replicar para TikTok)
        if "instagram" in perfiles_sociales:
            url_ig = perfiles_sociales["instagram"]
            try:
                # Usamos Apify para scrapear los últimos posts
                run_input = {
                    "directUrls": [url_ig],
                    "resultsLimit": 5,
                    "searchType": "hashtag" # Ajuste según actor
                }
                # Nota: Aquí se usaría el actor real 'apify/instagram-scraper'
                # Para este código, simularemos la lógica post-apify para no gastar tus créditos en pruebas
                # run = self.apify.actor("apify/instagram-scraper").call(run_input=run_input)
                # dataset = ... (obtener items)
                
                # --- SIMULACIÓN DE DATOS OBTENIDOS DE APIFY PARA LÓGICA ---
                ultimo_post_fecha = datetime.now() - timedelta(days=45) # Hace 45 días
                comentarios_simulados = [
                    "Precio?", 
                    "No responden al DM", 
                    "Info por favor"
                ]
                # -----------------------------------------------------------

                # 1. Verificar Frecuencia de Publicación (Regla: < 30 días)
                dias_sin_postear = (datetime.now() - ultimo_post_fecha).days
                if dias_sin_postear > 30:
                    dolores.append(f"REDES_ABANDONADAS_{dias_sin_postear}_DIAS")
                    logging.info(f"Detectado: Redes abandonadas hace {dias_sin_postear} días.")

                # 2. Análisis de Comentarios con IA (Regla: Respuestas lentas)
                if self.model and comentarios_simulados:
                    prompt = f"""
                    Eres un analista de atención al cliente. Lee estos comentarios de clientes en Instagram: {comentarios_simulados}.
                    Identifica si hay preguntas sin responder o quejas sobre lentitud.
                    Responde SOLO con 'SI' si detectas mala atención o 'NO' si todo está bien.
                    """
                    response = self.model.generate_content(prompt)
                    if "SI" in response.text.upper():
                        dolores.append("ATENCION_AL_CLIENTE_LENTA")

            except Exception as e:
                logging.error(f"Error analizando redes: {e}")

        return dolores

    # --- MÓDULO 3: ANÁLISIS REPUTACIÓN (GOOGLE MAPS) ---
    def analizar_reputacion(self, url_gmaps):
        """
        Extrae reseñas negativas y usa IA para categorizar la queja principal.
        """
        if not url_gmaps: return []
        
        dolores = []
        logging.info(f"⭐ Analizando Reputación en Gmaps: {url_gmaps}")

        try:
            # Llamada a Apify (Google Maps Scraper)
            # Limitamos a 10 reseñas para ahorrar y ser rápidos
            run_input = { "startUrls": [{ "url": url_gmaps }], "maxReviews": 10, "language": "es" }
            
            # actor_call = self.apify.actor("compass/crawler-google-places").call(run_input=run_input)
            # dataset_items = ...
            
            # --- SIMULACIÓN DE RESEÑAS NEGATIVAS ---
            resenas_negativas_texto = "Tardan mucho en servir. La comida llegó fría. Nadie atiende el teléfono."
            estrellas_promedio = 3.5
            # ---------------------------------------

            if estrellas_promedio < 4.0:
                dolores.append("BAJA_REPUTACION_ONLINE")

            # Análisis Cognitivo de la Queja Principal
            if self.model:
                prompt = f"""
                Analista de reputación. Lee estas reseñas negativas: "{resenas_negativas_texto}".
                Categoriza la queja principal en UNA de estas opciones exactas:
                [SERVICIO_LENTO, MALA_CALIDAD, PRECIOS_ALTOS, MALA_ATENCION, PROBLEMAS_RESERVAS].
                Solo devuelve la categoría.
                """
                res_ia = self.model.generate_content(prompt)
                categoria = res_ia.text.strip().replace(" ", "_").upper()
                dolores.append(f"DOLOR_{categoria}")

        except Exception as e:
            logging.error(f"Error en Gmaps: {e}")

        return dolores

    # --- ORQUESTACIÓN PRINCIPAL ---
    def procesar_lote(self):
        conn = self.conectar_db()
        cur = conn.cursor()

        try:
            # 1. Obtener prospecto 'cazado' (Bloqueo para evitar condiciones de carrera)
            cur.execute("""
                SELECT id, business_name, website_url, url_gmaps, social_profiles 
                FROM prospects 
                WHERE status = 'cazado' 
                LIMIT 1 
                FOR UPDATE SKIP LOCKED
            """)
            prospecto = cur.fetchone()

            if not prospecto:
                logging.info("💤 No hay prospectos nuevos para analizar. Durmiendo...")
                return

            pid, nombre, web, gmaps, sociales = prospecto
            logging.info(f"🚀 Iniciando análisis para: {nombre} (ID: {pid})")

            # Cambiar estado a 'analizando'
            cur.execute("UPDATE prospects SET status = 'analizando' WHERE id = %s", (pid,))
            conn.commit()

            # 2. Ejecutar Análisis Multi-Canal
            puntos_dolor = []
            inteligencia = {}

            # A. Web
            dolores_web, contactos = self.analizar_web(web)
            puntos_dolor.extend(dolores_web)
            if contactos["whatsapp"]: inteligencia["whatsapp_verificado"] = contactos["whatsapp"]
            
            # B. Redes Sociales
            # Parsear JSONB de sociales si viene como string o dict
            perfiles = sociales if isinstance(sociales, dict) else {}
            dolores_redes = self.analizar_redes(perfiles)
            puntos_dolor.extend(dolores_redes)

            # C. Reputación
            dolores_gmaps = self.analizar_reputacion(gmaps)
            puntos_dolor.extend(dolores_gmaps)

            # 3. Veredicto Final y Guardado
            nuevo_estado = 'analizado_exitoso' if puntos_dolor else 'analizado_descartado'
            
            # Construir JSON final
            resultado_analisis = {
                "puntos_de_dolor": puntos_dolor,
                "inteligencia_adicional": inteligencia,
                "fecha_analisis": datetime.now().isoformat()
            }

            logging.info(f"✅ Análisis completado. Dolores: {len(puntos_dolor)}. Estado: {nuevo_estado}")

            cur.execute("""
                UPDATE prospects 
                SET status = %s, 
                    pain_points = %s 
                WHERE id = %s
            """, (nuevo_estado, Json(resultado_analisis), pid))
            
            conn.commit()

        except Exception as e:
            logging.critical(f"❌ Error catastrófico analizando prospecto: {e}")
            if conn: conn.rollback()
        finally:
            cur.close()
            conn.close()

# --- PUNTO DE ENTRADA ---
if __name__ == "__main__":
    analista = TrabajadorAnalista()
    # En producción, esto podría estar en un bucle while True con time.sleep()
    analista.procesar_lote()
