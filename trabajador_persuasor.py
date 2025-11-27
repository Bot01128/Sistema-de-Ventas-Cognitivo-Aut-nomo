import os
import json
import logging
import secrets
import time
import psycopg2
from psycopg2.extras import Json
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIGURACIÓN ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - PERSUASOR - %(levelname)s - %(message)s')

DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Configuración IA
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    # CAMBIO 1: Usamos el modelo estable que sí tienes disponible para evitar error 404
    modelo_ia = genai.GenerativeModel('models/gemini-pro-latest')
else:
    logging.error("❌ SIN CEREBRO: GOOGLE_API_KEY no encontrada.")
    modelo_ia = None

def generar_contenido_persuasivo(nombre_prospecto, nombre_cliente, que_vende_cliente, puntos_dolor):
    """
    Usa Gemini para generar TODO el contenido personalizado.
    """
    dolor_principal = puntos_dolor[0] if puntos_dolor else "falta de optimización digital"
    # Convertimos lista a string para el prompt
    lista_dolores = ", ".join(puntos_dolor) if isinstance(puntos_dolor, list) else str(puntos_dolor)

    # Prompt diseñado para devolver JSON puro
    prompt = f"""
    Eres un experto en Copywriting Persuasivo y Ventas B2B.
    
    TUS DATOS:
    - Vendedor (Cliente): {nombre_cliente}
    - Producto/Servicio: {que_vende_cliente}
    - Prospecto (Comprador): {nombre_prospecto}
    - Dolor/Problema detectado: {lista_dolores}

    TU MISIÓN:
    Genera un objeto JSON con 3 textos persuasivos para un embudo de ventas.
    
    ESTRUCTURA DEL JSON REQUERIDA:
    {{
        "email_asunto": "Un asunto corto y curioso (max 7 palabras)",
        "email_cuerpo": "Un email corto (max 100 palabras). NO saludes con 'Espero que estés bien'. Ve al grano. Menciona el problema ({dolor_principal}) y diles que preparaste una demostración personalizada. El llamado a la acción es hacer clic en el enlace.",
        "prenido_titulo": "Un título impactante para la página web (Círculo Negro). Debe prometer una solución al {dolor_principal}.",
        "prenido_mensaje": "Un párrafo persuasivo (Círculo Azul). Explica que ya hiciste un análisis preliminar y detectaste una oportunidad. Diles que para ver el reporte completo y la demo, solo necesitan confirmar su correo abajo."
    }}

    IMPORTANTE: Responde SOLO con el JSON. Sin bloques de código markdown.
    """

    try:
        respuesta = modelo_ia.generate_content(prompt)
        texto_limpio = respuesta.text.strip().replace("```json", "").replace("```", "")
        return json.loads(texto_limpio)
    except Exception as e:
        logging.error(f"Error generando contenido con IA: {e}")
        return None

def trabajar_persuasor(limite_lote=5):
    """
    Busca prospectos 'analizados', genera su contenido y crea el token mágico.
    """
    logging.info("🧠 INICIANDO TURNO DE PERSUASIÓN")
    
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # 1. Obtener prospectos ANALIZADOS + Datos de la CAMPAÑA
        # CORRECCIÓN: Tablas en Inglés (prospects, campaigns) y columnas correctas (pain_points, campaign_name)
        query = """
            SELECT 
                p.id, 
                p.business_name, 
                p.pain_points,
                c.campaign_name, 
                c.product_description 
            FROM prospects p
            JOIN campaigns c ON p.campaign_id = c.id
            WHERE p.status = 'analizado_exitoso'
            LIMIT %s
            FOR UPDATE OF p SKIP LOCKED
        """
        cur.execute(query, (limite_lote,))
        lote = cur.fetchall()

        if not lote:
            logging.info("💤 No hay prospectos analizados esperando persuasión.")
            return

        logging.info(f"⚡ Procesando {len(lote)} prospectos para crear sus Nidos.")

        for fila in lote:
            pid, p_nombre, p_dolores, c_nombre, c_producto = fila
            
            # Parsear dolores si viene como string JSON o Dict
            dolores_lista = []
            if p_dolores:
                if isinstance(p_dolores, str):
                    try: 
                        data = json.loads(p_dolores)
                        dolores_lista = data.get("dolores_detectados", [])
                    except: pass
                elif isinstance(p_dolores, dict):
                     dolores_lista = p_dolores.get("dolores_detectados", [])

            # 2. Generar Contenido (Email + Landing)
            contenido = generar_contenido_persuasivo(p_nombre, c_nombre, c_producto, dolores_lista)

            if contenido:
                # 3. Generar TOKEN ÚNICO (La llave del Nido)
                token_unico = secrets.token_urlsafe(16)

                # 4. Guardar Todo
                # CORRECCIÓN: Columnas en Inglés (generated_content, access_token, status)
                update_query = """
                    UPDATE prospects
                    SET 
                        generated_content = %s,
                        access_token = %s,
                        status = 'persuadido',
                        updated_at = NOW()
                    WHERE id = %s
                """
                cur.execute(update_query, (Json(contenido), token_unico, pid))
                conn.commit()
                logging.info(f"✅ Prospecto {p_nombre} persuadido. Token: {token_unico}")
            else:
                logging.warning(f"⚠️ Fallo al generar IA para {p_nombre}")
            
            # CAMBIO 2: Pausa obligatoria para evitar error 429 (Cuota Excedida)
            logging.info("⏳ Pausando 5 segundos para respetar la cuota de Google...")
            time.sleep(5)

    except Exception as e:
        logging.critical(f"❌ Error catastrófico en Persuasor: {e}")
        if conn: conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()

# --- ENTRY POINT ---
if __name__ == "__main__":
    trabajar_persuasor()
