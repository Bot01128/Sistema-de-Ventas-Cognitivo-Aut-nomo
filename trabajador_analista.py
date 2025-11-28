import os
import time
import json
import logging
import requests
import psycopg2
from bs4 import BeautifulSoup
import google.generativeai as genai
from psycopg2.extras import Json
from dotenv import load_dotenv

# --- CONFIGURACIÓN ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - ANALISTA - %(levelname)s - %(message)s')

DATABASE_URL = os.environ.get("DATABASE_URL")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Configurar IA
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- 1. LECTURA DE WEB (OJOS DEL ANALISTA) ---

def escanear_web_simple(url):
    """
    Entra a la web del prospecto (si tiene) y extrae texto clave para análisis.
    Usa timeout corto para no perder tiempo.
    """
    if not url: return ""
    
    # Limpieza básica de URL
    if not url.startswith("http"): url = "http://" + url
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200: return ""
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraemos títulos y párrafos (lo más relevante)
        textos = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'meta']):
            if tag.name == 'meta' and tag.get('name') == 'description':
                textos.append(tag.get('content', ''))
            else:
                textos.append(tag.get_text(strip=True))
        
        # Unimos y cortamos para no saturar a Gemini (máx 2000 caracteres)
        contenido_limpio = " ".join(textos)[:2000]
        return contenido_limpio

    except Exception as e:
        logging.warning(f"No se pudo leer la web {url}: {e}")
        return ""

# --- 2. EL PSICÓLOGO (GEMINI) ---

def realizar_psicoanalisis(prospecto, campana, texto_web):
    """
    Envía los datos a Gemini para que juzgue y cree el plan de ataque.
    """
    
    # Preparamos el contexto para la IA
    prompt = f"""
    ERES UN ANALISTA DE VENTAS DE ÉLITE (PSICÓLOGO DE VENTAS).
    Tu misión es filtrar prospectos y crear estrategias de persuasión.
    
    --- DATOS DE LA CAMPAÑA (LO QUE VENDEMOS) ---
    Producto: {campana['product_description']}
    Precio (Ticket): {campana.get('ticket_price', 'No especificado')}
    Red Flags (A QUIÉN DESCARTAR): {campana.get('red_flags', 'Ninguna')}
    Dolores Definidos: {campana.get('pain_points_defined', 'General')}
    Competencia: {campana.get('competitors', 'Desconocida')}
    
    --- DATOS DEL PROSPECTO (A QUIÉN ANALIZAS) ---
    Nombre: {prospecto['business_name']}
    Web/Bio Info: {texto_web}
    Datos Crudos (JSON): {str(prospecto.get('raw_data', {}))[:1000]}
    
    --- TUS ÓRDENES ---
    1. FILTRO DE RED FLAGS: Si encuentras palabras prohibidas o el perfil no encaja (ej: estudiante para producto high-ticket), DESCÁRTALO.
    2. FILTRO DE PODER ADQUISITIVO: Analiza si pueden pagar el Ticket. (Web rota/inexistente + correo gratuito = Probable descarte si el ticket es alto).
    3. DETECCIÓN DE DOLORES: Busca evidencia de los dolores de la campaña en su info.
    4. PERFILADO: Infiere género, edad aprox y tono recomendado.

    --- SALIDA OBLIGATORIA (JSON PURO) ---
    Responde SOLO con este JSON:
    {{
        "veredicto": "APROBADO" o "DESCARTADO",
        "razon_descarte": "Texto explicativo si se descarta (o null)",
        "perfil_demografico": {{
            "genero_inferido": "Masculino/Femenino/Empresa",
            "edad_aprox": "20-30 / 40-50 / N/A",
            "tono_recomendado": "{campana.get('tone_voice', 'Profesional')}"
        }},
        "analisis_dolores": [
            {{
                "dolor_detectado": "Ej: Falta de tiempo",
                "evidencia": "Ej: Su web dice que tardan en responder",
                "plan_ataque": "Ej: Ofrecer automatización 24/7"
            }}
        ],
        "puntuacion_calidad": 0-100
    }}
    """

    try:
        respuesta = model.generate_content(prompt)
        # Limpieza de formato por si la IA pone ```json
        texto_limpio = respuesta.text.replace("```json", "").replace("```", "").strip()
        return json.loads(texto_limpio)
    except Exception as e:
        logging.error(f"Error interpretando a Gemini: {e}")
        return None

# --- 3. FUNCIÓN PRINCIPAL DEL TRABAJADOR ---

def trabajar_analista():
    """
    Ciclo infinito que busca prospectos 'espiado', los analiza y los clasifica.
    """
    logging.info("🧠 Analista Iniciado. Esperando pacientes...")
    
    while True:
        conn = None
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()

            # 1. Obtener Lote de Trabajo (JOIN con Campaña para tener contexto)
            # Buscamos prospectos 'espiado' (ya tienen contacto)
            query = """
                SELECT 
                    p.id, p.business_name, p.website_url, p.raw_data, p.captured_email,
                    c.id as campaign_id, c.product_description, c.ticket_price, 
                    c.red_flags, c.pain_points_defined, c.competitors, c.tone_voice
                FROM prospects p
                JOIN campaigns c ON p.campaign_id = c.id
                WHERE p.status = 'espiado'
                LIMIT 5;
            """
            cur.execute(query)
            lote = cur.fetchall()

            if not lote:
                logging.info("💤 Nada que analizar. Durmiendo 60s...")
                time.sleep(60) # Espera pasiva
                continue

            logging.info(f"🧠 Procesando lote de {len(lote)} prospectos...")

            for fila in lote:
                # Estructurar datos
                prospecto = {
                    "id": fila[0], "business_name": fila[1], "website_url": fila[2], 
                    "raw_data": fila[3], "email": fila[4]
                }
                campana = {
                    "product_description": fila[6], "ticket_price": fila[7],
                    "red_flags": fila[8], "pain_points_defined": fila[9],
                    "competitors": fila[10], "tone_voice": fila[11]
                }

                # A. Escaneo (Ojos)
                texto_web = ""
                if prospecto["website_url"]:
                    texto_web = escanear_web_simple(prospecto["website_url"])
                
                # B. Psicoanálisis (Cerebro)
                analisis_ia = realizar_psicoanalisis(prospecto, campana, texto_web)

                # C. Sentencia (Juez)
                nuevo_estado = "analizado_exitoso"
                pain_points_json = None

                if not analisis_ia:
                    # Si falla Gemini, lo dejamos para después o lo marcamos error
                    logging.warning(f"⚠️ Fallo análisis IA ID {prospecto['id']}")
                    continue 

                if analisis_ia.get("veredicto") == "DESCARTADO":
                    nuevo_estado = "descartado"
                    logging.info(f"🚫 DESCARTADO ID {prospecto['id']}: {analisis_ia.get('razon_descarte')}")
                else:
                    logging.info(f"✅ APROBADO ID {prospecto['id']}. Calidad: {analisis_ia.get('puntuacion_calidad')}")
                    pain_points_json = Json(analisis_ia)

                # D. Guardado en DB
                update_query = """
                    UPDATE prospects 
                    SET status = %s,
                        pain_points = %s,
                        updated_at = NOW()
                    WHERE id = %s
                """
                cur.execute(update_query, (nuevo_estado, pain_points_json, prospecto['id']))
                conn.commit()
                
                # Pausa anti-bloqueo Gemini (Plan Free)
                time.sleep(5) 

            cur.close()

        except Exception as e:
            logging.error(f"🔥 Error Crítico Analista: {e}")
            time.sleep(30)
        finally:
            if conn: conn.close()

if __name__ == "__main__":
    trabajar_analista()
