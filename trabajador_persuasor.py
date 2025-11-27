import os
import json
import logging
import secrets
import time  # <--- IMPORTANTE: Importamos time
import psycopg2
from psycopg2.extras import Json
import google.generativeai as genai
from dotenv import load_dotenv

# ... (CONFIGURACIÓN IGUAL QUE ANTES) ...
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - PERSUASOR - %(levelname)s - %(message)s')

DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    modelo_ia = genai.GenerativeModel('models/gemini-pro-latest')
else:
    logging.error("❌ SIN CEREBRO: GOOGLE_API_KEY no encontrada.")
    modelo_ia = None

# ... (FUNCIÓN generar_contenido_persuasivo IGUAL QUE ANTES) ...
def generar_contenido_persuasivo(nombre_prospecto, nombre_cliente, que_vende_cliente, puntos_dolor):
    # ... (El código de esta función no cambia) ...
    dolor_principal = puntos_dolor[0] if puntos_dolor else "falta de optimización digital"
    lista_dolores = ", ".join(puntos_dolor) if isinstance(puntos_dolor, list) else str(puntos_dolor)

    prompt = f"""
    Eres un experto en Copywriting Persuasivo y Ventas B2B.
    TUS DATOS:
    - Vendedor (Cliente): {nombre_cliente}
    - Producto/Servicio: {que_vende_cliente}
    - Prospecto (Comprador): {nombre_prospecto}
    - Dolor/Problema detectado: {lista_dolores}

    TU MISIÓN: Genera un objeto JSON con 3 textos persuasivos.
    ESTRUCTURA JSON: {{ "email_asunto": "...", "email_cuerpo": "...", "prenido_titulo": "...", "prenido_mensaje": "..." }}
    Responde SOLO JSON.
    """
    try:
        respuesta = modelo_ia.generate_content(prompt)
        texto_limpio = respuesta.text.strip().replace("```json", "").replace("```", "")
        return json.loads(texto_limpio)
    except Exception as e:
        logging.error(f"Error IA: {e}")
        return None

def trabajar_persuasor(limite_lote=5):
    logging.info("🧠 INICIANDO TURNO DE PERSUASIÓN")
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # 1. Obtener prospectos
        query = """
            SELECT p.id, p.business_name, p.pain_points, c.campaign_name, c.product_description 
            FROM prospects p
            JOIN campaigns c ON p.campaign_id = c.id
            WHERE p.status = 'analizado_exitoso'
            LIMIT %s
            FOR UPDATE OF p SKIP LOCKED
        """
        cur.execute(query, (limite_lote,))
        lote = cur.fetchall()

        if not lote:
            logging.info("💤 Nada para persuadir.")
            return

        logging.info(f"⚡ Procesando {len(lote)} prospectos...")

        for fila in lote:
            pid, p_nombre, p_dolores, c_nombre, c_producto = fila
            
            dolores_lista = []
            if p_dolores:
                if isinstance(p_dolores, str):
                    try: dolores_lista = json.loads(p_dolores).get("dolores_detectados", [])
                    except: pass
                elif isinstance(p_dolores, dict):
                     dolores_lista = p_dolores.get("dolores_detectados", [])

            # 2. Generar Contenido
            contenido = generar_contenido_persuasivo(p_nombre, c_nombre, c_producto, dolores_lista)

            if contenido:
                token_unico = secrets.token_urlsafe(16)
                update_query = """
                    UPDATE prospects
                    SET generated_content = %s, access_token = %s, status = 'persuadido', updated_at = NOW()
                    WHERE id = %s
                """
                cur.execute(update_query, (Json(contenido), token_unico, pid))
                conn.commit()
                logging.info(f"✅ Persuadido: {p_nombre}")
            else:
                logging.warning(f"⚠️ Fallo IA para {p_nombre}")

            # --- FRENO DE MANO PARA GOOGLE (NUEVO) ---
            logging.info("⏳ Esperando 5 segundos para no saturar a Google...")
            time.sleep(5) 

    except Exception as e:
        logging.critical(f"❌ Error Persuasor: {e}")
        if conn: conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    trabajar_persuasor()
