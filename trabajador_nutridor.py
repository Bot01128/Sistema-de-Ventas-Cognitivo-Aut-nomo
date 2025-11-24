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
    # 🧠 MODO CHAT (INTERACTIVO) - Llamado por main.py cuando el usuario escribe
    # ==============================================================================
    
    def responder_chat_nido(self, token_acceso, mensaje_usuario):
        """
        Esta función recibe el mensaje del chat del Nido, piensa la respuesta 
        basada en la campaña del cliente y devuelve el texto.
        También cuenta las interacciones para tu facturación.
        """
        logging.info(f"💬 Chat recibido en Nido (Token: {token_acceso})")
        conn = self.conectar_db()
        cur = conn.cursor()
        respuesta_final = "Lo siento, estoy teniendo problemas de conexión. Intenta de nuevo."

        try:
            # 1. Identificar Prospecto y Campaña usando el TOKEN
            query = """
                SELECT 
                    p.id, 
                    p.business_name, 
                    p.puntos_de_dolor, 
                    p.interacciones_nutridor,
                    c.nombre_negocio, 
                    c.descripcion_producto,
                    c.nombre_campana
                FROM prospects p
                JOIN campanas c ON p.campana_id = c.id
                WHERE p.token_acceso = %s
            """
            cur.execute(query, (token_acceso,))
            data = cur.fetchone()

            if not data:
                return "Error: Token de sesión inválido."

            pid, p_nombre, p_dolores, interacciones, c_cliente, c_producto, c_campana = data

            # Parsear dolores para contexto
            texto_dolores = ""
            if isinstance(p_dolores, dict):
                texto_dolores = ", ".join(p_dolores.get("dolores_detectados", []))

            # 2. Análisis de Intención (Psicología de Ventas)
            prompt_analisis = f"""
            Eres el Asistente de Ventas IA de '{c_cliente}'.
            Estás hablando con '{p_nombre}'.
            Producto que vendes: {c_producto}
            Dolores del prospecto: {texto_dolores}
            
            Mensaje del usuario: "{mensaje_usuario}"
            
            Instrucciones:
            Responde como un experto consultor. 
            1. Si pregunta precio y no lo tienes, vende el valor.
            2. Si pone una objeción, usa la técnica "Sentir, Comprendido, Encontrado" (Feel, Felt, Found).
            3. Si muestra interés de compra, invítalo a agendar o comprar.
            4. Sé breve (máximo 2 párrafos).
            5. Mantén un tono profesional pero cercano.
            """

            respuesta_ia = modelo_ia.generate_content(prompt_analisis)
            respuesta_final = respuesta_ia.text.strip()

            # 3. Registrar la Interacción (CRÍTICO PARA TU NEGOCIO)
            # Incrementamos el contador. Cuando llegue a 3, es un "Prospecto Válido".
            nuevo_conteo = (interacciones or 0) + 1
            cur.execute("""
                UPDATE prospects 
                SET interacciones_nutridor = %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (nuevo_conteo, pid))
            
            conn.commit()
            logging.info(f"✅ Respuesta generada. Interacciones acumuladas: {nuevo_conteo}")

        except Exception as e:
            logging.error(f"Error en Chat Nutridor: {e}")
            if conn: conn.rollback()
        finally:
            cur.close()
            conn.close()

        return respuesta_final

    # ==============================================================================
    # ♟️ MODO AJEDREZ (SEGUIMIENTO) - Llamado por el Orquestador cada 24h
    # ==============================================================================

    def ejecutar_ciclo_seguimiento(self):
        """
        Revisa prospectos inactivos y genera correos de seguimiento (Valor -> Prueba Social -> Despedida).
        """
        logging.info("♟️ Iniciando ronda de Seguimiento (Ajedrez)...")
        conn = self.conectar_db()
        cur = conn.cursor()

        try:
            # --- JUGADA 1: APORTE DE VALOR (Si lleva 3 días en 'persuadido') ---
            cur.execute("""
                SELECT p.id, p.business_name, p.puntos_de_dolor, c.descripcion_producto 
                FROM prospects p JOIN campanas c ON p.campana_id = c.id
                WHERE p.estado_prospecto = 'persuadido' 
                AND p.updated_at < NOW() - INTERVAL '3 DAYS'
            """)
            lote_1 = cur.fetchall()
            for row in lote_1:
                self._generar_y_guardar_email(cur, row, "VALOR", "en_nutricion_1")

            # --- JUGADA 2: PRUEBA SOCIAL (Si lleva 4 días en 'en_nutricion_1') ---
            cur.execute("""
                SELECT p.id, p.business_name, p.puntos_de_dolor, c.descripcion_producto 
                FROM prospects p JOIN campanas c ON p.campana_id = c.id
                WHERE p.estado_prospecto = 'en_nutricion_1' 
                AND p.updated_at < NOW() - INTERVAL '4 DAYS'
            """)
            lote_2 = cur.fetchall()
            for row in lote_2:
                self._generar_y_guardar_email(cur, row, "PRUEBA_SOCIAL", "en_nutricion_2")

            # --- JUGADA 3: DESPEDIDA (Si lleva 5 días en 'en_nutricion_2') ---
            cur.execute("""
                SELECT p.id, p.business_name, p.puntos_de_dolor, c.descripcion_producto 
                FROM prospects p JOIN campanas c ON p.campana_id = c.id
                WHERE p.estado_prospecto = 'en_nutricion_2' 
                AND p.updated_at < NOW() - INTERVAL '5 DAYS'
            """)
            lote_3 = cur.fetchall()
            for row in lote_3:
                self._generar_y_guardar_email(cur, row, "DESPEDIDA", "lead_frio")

            conn.commit()
            logging.info("🏁 Ronda de seguimiento completada.")

        except Exception as e:
            logging.error(f"Error en ciclo de seguimiento: {e}")
            if conn: conn.rollback()
        finally:
            cur.close()
            conn.close()

    def _generar_y_guardar_email(self, cur, datos, tipo_jugada, nuevo_estado):
        """Función auxiliar privada para generar el email con IA y actualizar DB."""
        pid, nombre, dolores, producto = datos
        
        # Seleccionar Prompt según la jugada
        prompt = ""
        asunto_sugerido = ""
        
        if tipo_jugada == "VALOR":
            prompt = f"Escribe un email muy corto para {nombre}. Aporta un consejo rápido sobre {producto} sin vender. Tono servicial."
            asunto_sugerido = "Pensé en esto para tu negocio"
        elif tipo_jugada == "PRUEBA_SOCIAL":
            prompt = f"Escribe un email para {nombre}. Menciona que ayudaste a un cliente similar a tener éxito con {producto}. Tono inspirador."
            asunto_sugerido = "Resultados recientes"
        elif tipo_jugada == "DESPEDIDA":
            prompt = f"Escribe un email de despedida amable para {nombre}. Pregunta si cerrar su archivo. Tono profesional."
            asunto_sugerido = "¿Cerramos el expediente?"

        try:
            # Generar contenido
            res = modelo_ia.generate_content(prompt)
            cuerpo_email = res.text.strip()
            
            # Guardar en DB (Simulamos una cola de envíos o guardamos en borrador)
            # Aquí asumimos que tienes una tabla o columna para 'cola de correos' o actualizamos el ultimo borrador
            cur.execute("""
                UPDATE prospects 
                SET estado_prospecto = %s,
                    borrador_mensaje = %s, -- Guardamos el email para que otro sistema lo envíe
                    updated_at = NOW()
                WHERE id = %s
            """, (nuevo_estado, f"ASUNTO: {asunto_sugerido}\n\n{cuerpo_email}", pid))
            
            logging.info(f"📧 Email ({tipo_jugada}) generado para ID {pid}")
            
        except Exception as e:
            logging.error(f"Fallo generando email para {pid}: {e}")

# --- ENTRY POINT (PARA PRUEBAS) ---
if __name__ == "__main__":
    # Solo para probar el ciclo de seguimiento manualmente
    nutridor = TrabajadorNutridor()
    nutridor.ejecutar_ciclo_seguimiento()
