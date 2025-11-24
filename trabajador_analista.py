import os
import json
import logging
import time
import random
import requests
import psycopg2
from psycopg2.extras import Json
from datetime import datetime, timedelta
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
        1. Si la web existe (o error 404).
        2. Enlaces de WhatsApp (wa.me) o Email (mailto).
        3. Palabras clave que indiquen barreras de compra ("cotizar", "llamar").
        """
        dolores = []
        datos_contacto = {"whatsapp": None, "email": None}
        
        if not url:
            return ["SIN_SITIO_WEB"], datos_contacto

        logging.info(f"🔍 Analizando Sitio Web: {url}")
        try:
            # Simulamos ser un navegador real para evitar bloqueos simples
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code >= 400:
                return ["SITIO_WEB_ROTO_ERROR_404"], datos_contacto

            soup = BeautifulSoup(response.content, 'html.parser')

            # A. Búsqueda de WhatsApp (El Santo Grial del contacto)
            # Buscamos en todos los enlaces <a>
            wa_link = soup.find("a", href=lambda h: h and ("wa.me" in h or "api.whatsapp.com" in h))
            if wa_link:
                datos_contacto["whatsapp"] = wa_link['href']
                logging.info("✅ WhatsApp encontrado en la web.")
            else:
                dolores.append("SIN_ENLACE_WHATSAPP_DIRECTO") # Punto de dolor detectado

            # B. Búsqueda de Email
            mail_link = soup.find("a", href=lambda h: h and "mailto:" in h)
            if mail_link:
                datos_contacto["email"] = mail_link['href'].replace("mailto:", "")
            
            # C. Análisis Semántico Simple (Detectar complejidad de compra)
            texto_web = soup.get_text().lower()
            if "solicitar cotización" in texto_web or "llame para consultar precio" in texto_web:
                dolores.append("PRECIO_OCULTO_COMPRA_COMPLEJA")

        except Exception as e:
            logging.warning(f"⚠️ Web caída o inaccesible ({url}): {e}")
            return ["SITIO_WEB_INACCESIBLE"], datos_contacto

        return dolores, datos_contacto

    # --- MÓDULO 2: ANÁLISIS REDES SOCIALES (IA + APIFY) ---
    def analizar_redes(self, perfiles_sociales):
        """
        Si tiene perfil social, analiza la frecuencia de publicación y 
        usa la IA para leer el sentimiento de los comentarios (si hay presupuesto).
        """
        dolores = []
        
        if not perfiles_sociales or len(perfiles_sociales) == 0:
            return ["PRESENCIA_DIGITAL_NULA"]

        # Nota: Aquí podríamos usar Apify para obtener los últimos posts.
        # Para ahorrar en esta versión inicial, solo verificamos si tiene redes.
        # Si quisieras activar el scraper real de Instagram, descomentarías la llamada a Apify.
        
        # Lógica Simulada de "Último Post" (Para no gastar $49 solo probando)
        # En producción, esto se reemplazaría por `apify.actor("instagram-scraper").call(...)`
        # Si detectamos que no hay posts recientes:
        # dolores.append("REDES_ABANDONADAS")

        return dolores

    # --- MÓDULO 3: ANÁLISIS REPUTACIÓN CON IA (EL PSICÓLOGO) ---
    def analizar_reputacion_ia(self, nombre_negocio, reseñas_texto):
        """
        Usa Gemini para leer reseñas (simuladas o reales) y diagnosticar el problema principal.
        """
        if not modelo_ia or not reseñas_texto:
            return []

        dolores = []
        try:
            prompt = f"""
            Actúa como un consultor de negocios experto. Analiza estas reseñas negativas recientes de '{nombre_negocio}':
            "{reseñas_texto}"
            
            Identifica la causa raíz de la insatisfacción. Elige UNA SOLA categoría de esta lista:
            [ATENCION_LENTA, PRECIOS_ALTOS, MALA_CALIDAD, PROBLEMAS_ADMINISTRATIVOS, SITIO_FEO].
            
            Responde SOLO con la categoría.
            """
            
            respuesta = modelo_ia.generate_content(prompt)
            categoria = respuesta.text.strip().upper().replace(" ", "_")
            
            # Validar que la respuesta sea una de nuestras categorías
            if categoria in ["ATENCION_LENTA", "PRECIOS_ALTOS", "MALA_CALIDAD", "PROBLEMAS_ADMINISTRATIVOS", "SITIO_FEO"]:
                dolores.append(f"PAIN_POINT_{categoria}")
                logging.info(f"🧠 IA Diagnóstico: El cliente sufre de {categoria}")
            
        except Exception as e:
            logging.error(f"Error consultando a Gemini: {e}")
        
        return dolores

    # --- ORQUESTACIÓN PRINCIPAL ---
    def procesar_lote_prospectos(self, limite=5):
        """
        Toma 5 prospectos 'cazados', los analiza a fondo y guarda los resultados.
        """
        conn = self.conectar_db()
        cur = conn.cursor()

        try:
            # 1. Obtener prospectos 'cazados' (Bloqueo seguro con SKIP LOCKED)
            # Esto permite que varios analistas trabajen sin pisarse
            cur.execute("""
                SELECT id, business_name, website_url, social_profiles, datos_json
                FROM prospects 
                WHERE estado_prospecto = 'cazado' 
                LIMIT %s 
                FOR UPDATE SKIP LOCKED
            """, (limite,))
            
            lote = cur.fetchall()

            if not lote:
                logging.info("💤 No hay prospectos 'cazados' esperando análisis. Todo limpio.")
                return

            logging.info(f"🚀 Iniciando análisis de lote: {len(lote)} prospectos.")

            for prospecto in lote:
                pid, nombre, web, sociales, datos_extra = prospecto
                
                # Marcar como 'en_analisis' para que nadie más lo toque
                cur.execute("UPDATE prospects SET estado_prospecto = 'en_analisis' WHERE id = %s", (pid,))
                conn.commit()

                puntos_dolor = []
                inteligencia_extra = {}

                # A. Análisis Web (Rápido y Gratis)
                dolores_web, contactos_web = self.analizar_web(web)
                puntos_dolor.extend(dolores_web)
                
                # Si encontramos un WhatsApp en la web que no teníamos, lo guardamos
                if contactos_web["whatsapp"]:
                    inteligencia_extra["whatsapp_verificado"] = contactos_web["whatsapp"]
                    # Opcional: Actualizar el campo phone_number si estaba vacío
                    cur.execute("UPDATE prospects SET phone_number = COALESCE(phone_number, %s) WHERE id = %s", (contactos_web["whatsapp"], pid))

                # B. Análisis Redes (Presencia)
                if isinstance(sociales, str): sociales = json.loads(sociales) # Asegurar formato dict
                dolores_redes = self.analizar_redes(sociales)
                puntos_dolor.extend(dolores_redes)

                # C. Análisis IA (Si hay reseñas en los datos brutos del cazador)
                # A veces el cazador trae reseñas en 'datos_json'. Si las hay, las usamos.
                if datos_extra and 'reviews' in datos_extra:
                    dolores_ia = self.analizar_reputacion_ia(nombre, datos_extra['reviews'])
                    puntos_dolor.extend(dolores_ia)

                # D. Veredicto Final
                nuevo_estado = 'analizado_exitoso'
                if not web and not sociales:
                    # Si no tiene web ni redes, es un prospecto muy pobre (o muy difícil)
                    # Podemos descartarlo o dejarlo como 'analizado_baja_calidad'
                    nuevo_estado = 'analizado_baja_calidad'

                # Construir el JSON final de inteligencia
                informe_analisis = {
                    "fecha": datetime.now().isoformat(),
                    "dolores_detectados": puntos_dolor,
                    "inteligencia_extra": inteligencia_extra,
                    "score_calidad": 100 - (len(puntos_dolor) * 10) # Ejemplo simple de scoring
                }

                # Guardar en Base de Datos
                logging.info(f"💾 Guardando análisis para ID {pid}. Estado: {nuevo_estado}")
                cur.execute("""
                    UPDATE prospects 
                    SET estado_prospecto = %s, 
                        puntos_de_dolor = %s 
                    WHERE id = %s
                """, (nuevo_estado, Json(informe_analisis), pid))
                
                conn.commit()
                
                # Pequeña pausa para no saturar
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
    # Ejecutamos una ronda de análisis
    analista.procesar_lote_prospectos()
