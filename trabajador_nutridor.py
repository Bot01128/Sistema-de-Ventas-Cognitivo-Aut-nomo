import os
import json
import logging
import psycopg2
from psycopg2.extras import Json
import google.generativeai as genai
from datetime import datetime, timedelta
from dotenv import load_dotenv

# --- CONFIGURACIÓN ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - NUTRIDOR - %(levelname)s - %(message)s')

DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    modelo_ia = genai.GenerativeModel('gemini-1.5-flash')
else:
    logging.error("❌ SIN CEREBRO: GOOGLE_API_KEY no encontrada.")
    modelo_ia = None

class TrabajadorNutridor:
    def __init__(self):
        self.db_url = DATABASE_URL

    def conectar_db(self):
        return psycopg2.connect(self.db_url)

    # ==============================================================================
    # 🧠 MODO CHAT (INTERACTIVO)
    # ==============================================================================
    
    def responder_chat_nido(self, token_acceso, mensaje_usuario):
        """
        Responde al chat del Nido y cuenta interacciones.
        """
        logging.info(f"💬 Chat recibido en Nido (Token: {token_acceso})")
        conn = self.conectar_db()
        cur = conn.cursor()
        respuesta_final = "Lo siento, estoy teniendo problemas de conexión. Intenta de nuevo."

        try:
            # CORRECCIÓN: Tablas y Columnas en Inglés
            query = """
                SELECT 
                    p.id, 
                    p.business_name, 
                    p.pain_points, 
                    p.nurture_interactions_count,
                    c.campaign_name, 
                    c.product_description,
                    c.campaign_name
                FROM prospects p
                JOIN campaigns c ON p.campaign_id = c.id
                WHERE p.access_token = %s
            """
            cur.execute(query, (token_acceso,))
            data = cur.fetchone()

            if not data:
                return "Error: Token de sesión inválido."

            pid, p_nombre, p_dolores, interacciones, c_cliente, c_producto, c_campana = data

            # Parsear dolores
            texto_dolores = ""
            if p_dolores:
                if isinstance(p_dolores, dict):
                    texto_dolores = ", ".join(p_dolores.get("dolores_detectados", []))
                elif isinstance(p_dolores, str):
                    try: texto_dolores = ", ".join(json.loads(p_dolores).get("dolores_detectados", []))
                    except: pass

            # Prompt IA
            prompt_analisis = f"""
            Eres el Asistente de Ventas IA de '{c_cliente}'.
            Estás hablando con '{p_nombre}'.
            Producto que vendes: {c_producto}
            Dolores del prospecto: {texto_dolores}
            Mensaje del usuario: "{mensaje_usuario}"
            Instrucciones: Responde como experto consultor, sé breve y profesional.
            """

            respuesta_ia = modelo_ia.generate_content(prompt_analisis)
            respuesta_final = respuesta_ia.text.strip()

            # CORRECCIÓN: Actualizar contador 'nurture_interactions_count'
            nuevo_conteo = (interacciones or 0) + 1
            cur.execute("""
                UPDATE prospects 
                SET nurture_interactions_count = %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (nuevo_conteo, pid))
            
            conn.commit()
            logging.info(f"✅ Respuesta generada. Interacciones: {nuevo_conteo}")

        except Exception as e:
            logging.error(f"Error en Chat Nutridor: {e}")
            if conn: conn.rollback()
        finally:
            cur.close()
            conn.close()

        return respuesta_final

    # ==============================================================================
    # ♟️ MODO AJEDREZ (SEGUIMIENTO)
    # ==============================================================================

    def ejecutar_ciclo_seguimiento(self):
        logging.info("♟️ Iniciando ronda de Seguimiento (Ajedrez)...")
        conn = self.conectar_db()
        cur = conn.cursor()

        try:
            # CORRECCIÓN: Tablas y Columnas en Inglés
            # JUGADA 1: APORTE DE VALOR
            cur.execute("""
                SELECT p.id, p.business_name, p.pain_points, c.product_description 
                FROM prospects p JOIN campaigns c ON p.campaign_id = c.id
                WHERE p.status = 'persuadido' 
                AND p.updated_at < NOW() - INTERVAL '3 DAYS'
            """)
            for row in cur.fetchall():
                self._generar_y_guardar_email(cur, row, "VALOR", "en_nutricion_1")

            # JUGADA 2: PRUEBA SOCIAL
            cur.execute("""
                SELECT p.id, p.business_name, p.pain_points, c.product_description 
                FROM prospects p JOIN campaigns c ON p.campaign_id = c.id
                WHERE p.status = 'en_nutricion_1' 
                AND p.updated_at < NOW() - INTERVAL '4 DAYS'
            """)
            for row in cur.fetchall():
                self._generar_y_guardar_email(cur, row, "PRUEBA_SOCIAL", "en_nutricion_2")

            # JUGADA 3: DESPEDIDA
            cur.execute("""
                SELECT p.id, p.business_name, p.pain_points, c.product_description 
                FROM prospects p JOIN campaigns c ON p.campaign_id = c.id
                WHERE p.status = 'en_nutricion_2' 
                AND p.updated_at < NOW() - INTERVAL '5 DAYS'
            """)
            for row in cur.fetchall():
                self._generar_y_guardar_email(cur, row, "DESPEDIDA", "lead_frio")

            conn.commit()
            logging.info("🏁 Ronda de seguimiento completada.")

        except Exception as e:
            logging.error(f"Error en ciclo de seguimiento: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    def _generar_y_guardar_email(self, cur, datos, tipo_jugada, nuevo_estado):
        pid, nombre, dolores, producto = datos
        prompt = ""
        asunto = ""
        
        if tipo_jugada == "VALOR":
            prompt = f"Escribe email corto para {nombre}. Consejo sobre {producto}. Tono servicial."
            asunto = "Pensé en esto para ti"
        elif tipo_jugada == "PRUEBA_SOCIAL":
            prompt = f"Escribe email para {nombre}. Caso de éxito anónimo con {producto}. Tono inspirador."
            asunto = "Resultados recientes"
        elif tipo_jugada == "DESPEDIDA":
            prompt = f"Escribe email despedida amable para {nombre}. Preguntar si cerrar archivo."
            asunto = "¿Cerramos el expediente?"

        try:
            res = modelo_ia.generate_content(prompt)
            # CORRECCIÓN: 'status' y 'draft_message'
            cur.execute("""
                UPDATE prospects 
                SET status = %s,
                    draft_message = %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (nuevo_estado, f"ASUNTO: {asunto}\n\n{res.text}", pid))
            
            logging.info(f"📧 Email ({tipo_jugada}) generado para ID {pid}")
        except Exception as e:
            logging.error(f"Fallo generando email para {pid}: {e}")

# --- ENTRY POINT ---
if __name__ == "__main__":
    n = TrabajadorNutridor()
    n.ejecutar_ciclo_seguimiento()
