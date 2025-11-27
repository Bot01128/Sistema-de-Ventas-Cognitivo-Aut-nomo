import os
import time
import json
import logging
import psycopg2
import threading
import random  # <--- NECESARIO PARA LA ROTACIÓN
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
    print(f"!!! ERROR CRÍTICO: Faltan archivos. {e}")

# --- CONFIGURACIÓN ---
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ORQUESTADOR - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("sistema_autoneura.log"), logging.StreamHandler()]
)

DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    modelo_estrategico = genai.GenerativeModel('models/gemini-pro-latest')
else:
    modelo_estrategico = None

class OrquestadorSupremo:
    def __init__(self):
        self.analista = TrabajadorAnalista()
        self.nutridor = TrabajadorNutridor()
        
    def conectar_db(self):
        return psycopg2.connect(DATABASE_URL)

    def gestionar_finanzas_clientes(self):
        logging.info("💼 Revisando finanzas...")
        conn = self.conectar_db()
        try:
            # Lógica simplificada para mantener activos a los clientes con saldo
            with conn.cursor() as cur:
                cur.execute("UPDATE clients SET is_active = TRUE WHERE balance > 0 OR plan_cost > 0")
            conn.commit()
        except: pass
        finally: conn.close()

    # ==============================================================================
    # 🧠 ESTRATEGIA DE MERCADO (CON ROTACIÓN INTELIGENTE)
    # ==============================================================================

    def planificar_estrategia_caza(self, prod, audiencia, tipo_producto):
        """
        Define la plataforma y la query. AHORA ROTA LAS PLATAFORMAS.
        """
        # 1. Definir el "Menú" de opciones según el producto
        opciones = ["Google Maps"] # Maps siempre es útil para B2B
        
        if "intangible" in str(tipo_producto).lower() or "software" in str(prod).lower():
            opciones.extend(["TikTok", "Instagram"])
        
        # 2. ROTACIÓN: Elegir una al azar para este ciclo (evita quedarse pegado)
        plataforma_elegida = random.choice(opciones)
        
        query_final = audiencia # Por defecto

        # 3. Refinar la Query con IA
        if modelo_estrategico:
            prompt = f"""
            Actúa como Estratega de Marketing.
            Producto: {prod}
            Audiencia: {audiencia}
            Plataforma elegida: {plataforma_elegida}
            
            DAME SOLO UNA QUERY DE BÚSQUEDA OPTIMIZADA.
            - Si es Google Maps: "Rubro en Ciudad" (ej: Inmobiliarias en Miami).
            - Si es TikTok/Instagram: "Hashtag" (ej: #RealEstate).
            
            Responde SOLO el texto de la query. Nada más.
            """
            try:
                res = modelo_estrategico.generate_content(prompt)
                query_limpia = res.text.strip().replace('"', '').replace("'", "")
                if query_limpia and query_limpia.lower() != "none":
                    query_final = query_limpia
            except Exception as e:
                logging.warning(f"Fallo IA Estrategia: {e}. Usando default.")

        return query_final, plataforma_elegida

    def ejecutar_trabajador_cazador_thread(self, cid, query, ubic, plat, cant):
        try:
            logging.info(f"🧵 Hilo Caza: '{query}' en {plat}")
            # Si es Maps, necesitamos la ubicación en la query
            if plat == "Google Maps" and ubic and ubic not in query:
                query = f"{query} en {ubic}"
                
            ejecutar_caza(cid, query, ubic, plat, max_resultados=cant)
        except Exception as e:
            logging.error(f"Error hilo: {e}")

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
            logging.info(f"⚙️ Coordinando {len(campanas)} campañas...")

            for camp in campanas:
                cid, nom, prod, aud, tipo, cuota, ubic = camp
                
                # B. VERIFICAR
                cur.execute("SELECT COUNT(*) FROM prospects WHERE campaign_id = %s AND created_at::date = CURRENT_DATE", (cid,))
                hoy = cur.fetchone()[0]
                meta = (cuota or 4) * 3
                
                if hoy < meta:
                    # AQUÍ LLAMAMOS A LA ESTRATEGIA CON ROTACIÓN
                    q, plat = self.planificar_estrategia_caza(prod, aud, tipo)
                    
                    logging.info(f"🚀 Caza para '{nom}': Buscando '{q}' en {plat}")
                    
                    t = threading.Thread(
                        target=self.ejecutar_trabajador_cazador_thread, 
                        args=(cid, q, ubic, plat, meta - hoy)
                    )
                    t.start()
                    
                    logging.info("⏳ Esperando 10s para no saturar...")
                    time.sleep(10)
                else:
                    logging.info(f"✅ Campaña '{nom}' completa.")

            # C. CASCADA
            logging.info("🕵️ Analista...")
            self.analista.procesar_lote_prospectos(5)
            
            logging.info("✍️ Persuasor...")
            trabajar_persuasor(5)
            
            logging.info("♟️ Nutridor...")
            self.nutridor.ejecutar_ciclo_seguimiento()

        except Exception as e: logging.error(f"Error Ops: {e}")
        finally:
            cur.close()
            conn.close()

    def iniciar_turno(self):
        logging.info(">>> 🤖 ORQUESTADOR SUPREMO (ROTACIÓN ACTIVADA) 🤖 <<<")
        while True:
            try:
                self.gestionar_finanzas_clientes()
                self.coordinar_operaciones_diarias()
                logging.info("💤 Durmiendo 10 min...")
                time.sleep(600)
            except KeyboardInterrupt: break
            except Exception as e:
                logging.critical(f"🔥 Error Main: {e}")
                time.sleep(60)

if __name__ == "__main__":
    OrquestadorSupremo().iniciar_turno()
