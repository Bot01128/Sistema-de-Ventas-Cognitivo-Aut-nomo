import os
import time
import json
import logging
import psycopg2
import threading
from datetime import datetime, timedelta
from psycopg2.extras import Json
import google.generativeai as genai
from dotenv import load_dotenv

# --- IMPORTACIÓN DE TUS EMPLEADOS ---
try:
    from trabajador_cazador import ejecutar_caza
    from trabajador_analista import TrabajadorAnalista
    from trabajador_persuasor import trabajar_persuasor
    from trabajador_nutridor import TrabajadorNutridor
except ImportError as e:
    print(f"!!! ERROR CRÍTICO DE INICIO: Faltan archivos de trabajadores. Detalle: {e}")

# --- CONFIGURACIÓN ---
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ORQUESTADOR (CEO) - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("sistema_autoneura.log"), logging.StreamHandler()]
)

DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    modelo_estrategico = genai.GenerativeModel('gemini-1.5-flash')
else:
    logging.warning("⚠️ CEREBRO DESCONECTADO: No hay API Key.")
    modelo_estrategico = None

class OrquestadorSupremo:
    def __init__(self):
        self.analista = TrabajadorAnalista()
        self.nutridor = TrabajadorNutridor()
        
    def conectar_db(self):
        return psycopg2.connect(DATABASE_URL)

    def gestionar_finanzas_clientes(self):
        logging.info("💼 Revisando estado de cuentas...")
        conn = self.conectar_db()
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, email, balance, plan_type FROM clients WHERE is_active = TRUE")
            # Aquí iría la lógica de cobro real. Por ahora es passthrough.
            pass
        except Exception as e:
            logging.error(f"Error finanzas: {e}")
        finally:
            cur.close()
            conn.close()

    # --- CEREBRO: SELECCIÓN DE ESTRATEGIA ---
    def planificar_estrategia_caza(self, prod, audiencia, tipo_prod):
        """
        Decide QUÉ buscar y DÓNDE buscar (Maps, TikTok, Instagram).
        """
        platform_default = "Google Maps"
        query_default = audiencia

        # Reglas de Negocio Simples (Backup si falla la IA)
        if tipo_prod == "Intangible" or "software" in prod.lower():
            platform_default = "TikTok" # Mejor para B2B moderno/emprendedores
        
        if not modelo_estrategico: 
            return query_default, platform_default

        prompt = f"""
        Eres un Estratega de Marketing B2B.
        PRODUCTO: {prod}
        AUDIENCIA: {audiencia}
        TIPO: {tipo_prod} (Tangible = Físico, Intangible = Servicio/Digital)
        
        TU MISIÓN:
        1. Elige la mejor plataforma para encontrar a estos clientes: 'Google Maps' (Negocios Locales), 'TikTok' (Emprendedores/Marcas Personales) o 'Instagram' (Influencers/Tiendas).
        2. Define la 'Query' de búsqueda exacta.
        
        Output JSON: {{"query": "...", "platform": "..."}}
        """
        try:
            res = modelo_estrategico.generate_content(prompt)
            data = json.loads(res.text.replace("```json", "").replace("```", "").strip())
            return data.get("query", query_default), data.get("platform", platform_default)
        except: 
            return query_default, platform_default

    def ejecutar_trabajador_cazador_thread(self, cid, query, ubic, plat, cant):
        try:
            # Llama al Cazador con la plataforma elegida
            logging.info(f"🧵 Hilo de Caza iniciado para Campaña {cid} en {plat}")
            ejecutar_caza(cid, query, ubic, plat, tipo_producto="Variable", max_resultados=cant)
        except Exception as e:
            logging.error(f"Error en hilo de caza {cid}: {e}")

    def coordinar_operaciones_diarias(self):
        conn = self.conectar_db()
        cur = conn.cursor()
        try:
            # A. CAMPAÑAS ACTIVAS
            cur.execute("""
                SELECT c.id, c.campaign_name, c.product_description, c.target_audience, 
                       c.product_type, cl.daily_prospects_quota, c.geo_location
                FROM campaigns c JOIN clients cl ON c.client_id = cl.id
                WHERE c.status = 'active' AND cl.is_active = TRUE
            """)
            campanas = cur.fetchall()
            logging.info(f"⚙️ Coordinando {len(campanas)} campañas activas...")

            for camp in campanas:
                camp_id, nombre, prod, audiencia, tipo, cuota, ubic = camp
                
                # B. VERIFICAR PROGRESO
                cur.execute("SELECT COUNT(*) FROM prospects WHERE campaign_id = %s AND created_at::date = CURRENT_DATE", (camp_id,))
                cazados_hoy = cur.fetchone()[0]
                meta_caza = (cuota or 4) * 3 # Factor 3x
                
                if cazados_hoy < meta_caza:
                    faltantes = meta_caza - cazados_hoy
                    
                    # 1. PENSAR (Estrategia con IA)
                    q_opt, plat = self.planificar_estrategia_caza(prod, audiencia, tipo)
                    
                    logging.info(f"🚀 Caza para '{nombre}'. Faltan {faltantes}. Query: '{q_opt}' en {plat}")
                    
                    # 2. CAZAR (Thread)
                    t = threading.Thread(target=self.ejecutar_trabajador_cazador_thread, args=(camp_id, q_opt, ubic, plat, faltantes))
                    t.start()
                else:
                    logging.info(f"✅ Campaña '{nombre}' completa ({cazados_hoy}/{meta_caza}).")

            # C. CASCADA DE PROCESOS (Lotes Pequeños)
            logging.info("🕵️ Analista...")
            self.analista.procesar_lote_prospectos(limite=5)
            
            logging.info("✍️ Persuasor...")
            trabajar_persuasor(limite_lote=5)
            
            logging.info("♟️ Nutridor...")
            self.nutridor.ejecutar_ciclo_seguimiento()

        except Exception as e:
            logging.error(f"Error operaciones: {e}")
        finally:
            cur.close()
            conn.close()

    def iniciar_turno(self):
        logging.info(">>> 🤖 ORQUESTADOR SUPREMO V3 (MULTI-PLATAFORMA) 🤖 <<<")
        while True:
            try:
                self.gestionar_finanzas_clientes()
                self.coordinar_operaciones_diarias()
                
                # DESCANSO DE 10 MINUTOS (Vital para Apify)
                logging.info("💤 Ciclo finalizado. Durmiendo 10 minutos...")
                time.sleep(600) 
            except KeyboardInterrupt: break
            except Exception as e:
                logging.critical(f"🔥 ERROR MAIN LOOP: {e}")
                time.sleep(60)

if __name__ == "__main__":
    ceo = OrquestadorSupremo()
    ceo.iniciar_turno()
