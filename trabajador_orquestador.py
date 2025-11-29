import os
import time
import json
import logging
import psycopg2
import threading
import random
from datetime import datetime, timedelta
from psycopg2.extras import Json
import google.generativeai as genai
from dotenv import load_dotenv

# --- IMPORTACIÓN DE TUS EMPLEADOS (LOS TRABAJADORES) ---
try:
    # Trabajadores tipo "Función Única" (Cazador y Espía)
    from trabajador_cazador import ejecutar_caza
    from trabajador_espia import ejecutar_espia
    
    # Trabajadores tipo "Bucle Infinito" (Analista y Persuasor)
    from trabajador_analista import trabajar_analista
    from trabajador_persuasor import trabajar_persuasor
    
    # Trabajador tipo "Clase" (Nutridor)
    from trabajador_nutridor import TrabajadorNutridor
except ImportError as e:
    print(f"!!! ERROR CRÍTICO DE INICIO: Faltan archivos de trabajadores. Detalle: {e}")

# --- CONFIGURACIÓN ---
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ORQUESTADOR (CEO) - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sistema_autoneura.log"),
        logging.StreamHandler()
    ]
)

DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Configuración del Cerebro Estratégico
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    # MODELO RÁPIDO PARA EL ORQUESTADOR
    MODELO_ESTRATEGICO_ID = 'models/gemini-2.0-flash'
    modelo_estrategico = genai.GenerativeModel(MODELO_ESTRATEGICO_ID)
    logging.info(f"🧠 Cerebro conectado usando: {MODELO_ESTRATEGICO_ID}")
else:
    logging.warning("⚠️ CEREBRO DESCONECTADO: No hay API Key de Google. El Orquestador será menos inteligente.")
    modelo_estrategico = None

class OrquestadorSupremo:
    def __init__(self):
        # Inicializamos solo al Nutridor aquí, los demás son funciones autónomas
        self.nutridor = TrabajadorNutridor()
        
    def conectar_db(self):
        return psycopg2.connect(DATABASE_URL)

    # ==============================================================================
    # 💰 MÓDULO 1: DEPARTAMENTO FINANCIERO
    # ==============================================================================

    def gestionar_finanzas_clientes(self):
        """Revisa pagos, envía alertas y corta el servicio a morosos."""
        logging.info("💼 Revisando estado de cuentas y pagos...")
        conn = self.conectar_db()
        cur = conn.cursor()
        
        try:
            # 1. ALERTA DE PAGO PRÓXIMO
            cur.execute("""
                SELECT id, email, full_name, next_payment_date 
                FROM clients 
                WHERE is_active = TRUE 
                AND next_payment_date BETWEEN NOW() AND NOW() + INTERVAL '3 DAYS'
                AND payment_alert_sent = FALSE
            """)
            for c in cur.fetchall():
                self.enviar_notificacion(c[1], "Tu suscripción vence pronto", f"Hola {c[2]}, recuerda recargar.")
                cur.execute("UPDATE clients SET payment_alert_sent = TRUE WHERE id = %s", (c[0],))

            # 2. PROCESAMIENTO DE COBROS
            cur.execute("""
                SELECT id, email, balance, plan_cost 
                FROM clients 
                WHERE is_active = TRUE AND next_payment_date <= NOW()
            """)
            for c in cur.fetchall():
                cid, email, saldo, costo = c or (0, "", 0, 0)
                costo = costo or 0
                
                if saldo and saldo >= costo:
                    nuevo_saldo = saldo - costo
                    cur.execute("""
                        UPDATE clients 
                        SET balance = %s, next_payment_date = next_payment_date + INTERVAL '30 DAYS', payment_alert_sent = FALSE 
                        WHERE id = %s
                    """, (nuevo_saldo, cid))
                    logging.info(f"✅ Cobro exitoso: Cliente {cid}. Nuevo ciclo iniciado.")
                elif costo > 0:
                    cur.execute("UPDATE clients SET is_active = FALSE, status = 'suspended_payment_fail' WHERE id = %s", (cid,))
                    self.enviar_notificacion(email, "Servicio Suspendido", "No tienes saldo suficiente.")
                    logging.warning(f"⛔ Cliente {cid} suspendido por falta de fondos.")

            conn.commit()

        except Exception as e:
            logging.error(f"Error crítico en finanzas: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    # ==============================================================================
    # 🧠 MÓDULO 2: ESTRATEGIA DE MERCADO
    # ==============================================================================

    def planificar_estrategia_caza(self, descripcion_producto, audiencia_objetivo, tipo_producto):
        """Define si buscar en Maps, TikTok o Instagram y qué palabra clave usar."""
        opciones = ["Google Maps"]
        if "intangible" in str(tipo_producto).lower() or "software" in str(descripcion_producto).lower():
            opciones.extend(["TikTok", "Instagram"])
        
        platform_default = random.choice(opciones)
        query_default = audiencia_objetivo

        if not modelo_estrategico:
            return query_default, platform_default

        prompt = f"""
        Eres un Estratega de Marketing B2B.
        PRODUCTO: {descripcion_producto}
        AUDIENCIA DESEADA: {audiencia_objetivo}
        TIPO: {tipo_producto}
        
        TU MISIÓN:
        1. Elige la mejor plataforma para este ciclo: 'Google Maps', 'TikTok' o 'Instagram'.
        2. Define la 'Query' de búsqueda optimizada.
        
        Responde SOLO con un JSON: {{"query": "...", "platform": "..."}}
        """
        try:
            res = modelo_estrategico.generate_content(prompt)
            data = json.loads(res.text.replace("```json", "").replace("```", "").strip())
            return data.get("query", query_default), data.get("platform", platform_default)
        except:
            return query_default, platform_default

    # ==============================================================================
    # ⚙️ MÓDULO 3: COORDINACIÓN DE TRABAJADORES
    # ==============================================================================

    def ejecutar_trabajador_cazador_thread(self, cid, query, ubic, plat, limite_diario):
        """Lanza el Cazador en un hilo paralelo."""
        try:
            logging.info(f"🧵 Hilo de Caza iniciado para Campaña {cid} en {plat}")
            # Llama al Cazador nuevo con el parámetro correcto de límite diario
            ejecutar_caza(cid, query, ubic, plat, tipo_producto="Variable", limite_diario_contratado=limite_diario)
        except Exception as e:
            logging.error(f"Error en hilo de caza {cid}: {e}")

    def ejecutar_trabajador_espia_thread(self, cid, limite_diario):
        """Lanza el Espía en un hilo paralelo."""
        try:
            logging.info(f"🧵 Hilo de Espionaje iniciado para Campaña {cid}")
            ejecutar_espia(cid, limite_diario_contratado=limite_diario)
        except Exception as e:
            logging.error(f"Error en hilo de espía {cid}: {e}")

    def coordinar_operaciones_diarias(self):
        """Verifica metas diarias y activa a los trabajadores."""
        conn = self.conectar_db()
        cur = conn.cursor()
        
        try:
            # A. OBTENER CAMPAÑAS ACTIVAS (Leyendo daily_prospects_limit)
            cur.execute("""
                SELECT c.id, c.campaign_name, c.product_description, c.target_audience, 
                       c.product_type, c.daily_prospects_limit, c.geo_location
                FROM campaigns c
                JOIN clients cl ON c.client_id = cl.id
                WHERE c.status = 'active' AND cl.is_active = TRUE
            """)
            campanas_activas = cur.fetchall()
            
            logging.info(f"⚙️ Coordinando {len(campanas_activas)} campañas activas...")

            for camp in campanas_activas:
                camp_id, nombre, prod, audiencia, tipo_prod, limite_diario, ubicacion = camp
                
                # Default de seguridad
                if not limite_diario: limite_diario = 4

                # B. VERIFICAR PROGRESO
                cur.execute("""
                    SELECT COUNT(*) FROM prospects 
                    WHERE campaign_id = %s 
                    AND created_at::date = CURRENT_DATE
                    AND status = 'cazado'
                """, (camp_id,))
                
                cazados_hoy = cur.fetchone()[0]
                
                logging.info(f"📊 Estado '{nombre}': {cazados_hoy} cazados hoy. Activando trabajadores...")

                # 1. PENSAR ESTRATEGIA (IA)
                query_optimizada, plataforma = self.planificar_estrategia_caza(prod, audiencia, tipo_prod)
                
                # 2. LANZAR CAZADOR (Thread)
                t_caza = threading.Thread(
                    target=self.ejecutar_trabajador_cazador_thread,
                    args=(camp_id, query_optimizada, ubicacion, plataforma, limite_diario)
                )
                t_caza.start()

                # 3. LANZAR ESPÍA (Thread)
                t_espia = threading.Thread(
                    target=self.ejecutar_trabajador_espia_thread,
                    args=(camp_id, limite_diario)
                )
                t_espia.start()
                
                time.sleep(2)

            # C. EL NUTRIDOR
            logging.info("♟️ Despertando al Nutridor...")
            self.nutridor.ejecutar_ciclo_seguimiento()

        except Exception as e:
            logging.error(f"Error en coordinación operaciones: {e}")
        finally:
            cur.close()
            conn.close()

    # ==============================================================================
    # 📨 MÓDULO 4: REPORTES Y COMUNICACIÓN
    # ==============================================================================

    def enviar_notificacion(self, email, asunto, mensaje):
        logging.info(f"📧 [SIMULACION EMAIL] A: {email} | Asunto: {asunto}")

    def generar_reporte_diario(self):
        conn = self.conectar_db()
        cur = conn.cursor()
        logging.info("📊 Generando reportes diarios...")
        
        try:
            cur.execute("SELECT id, email, full_name FROM clients WHERE is_active = TRUE")
            clientes = cur.fetchall()
            
            for c in clientes:
                cid, email, nombre = c
                
                # --- CORRECCIÓN CRÍTICA DE SQL AQUÍ ---
                # Usamos 'p.status' para evitar la ambigüedad
                cur.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE p.status='cazado') as nuevos,
                        COUNT(*) FILTER (WHERE p.status='persuadido') as listos_nutrir
                    FROM prospects p
                    JOIN campaigns cam ON p.campaign_id = cam.id
                    WHERE cam.client_id = %s 
                    AND p.created_at >= NOW() - INTERVAL '24 HOURS'
                """, (cid,))
                stats = cur.fetchone()
                
                if stats:
                    cuerpo = f"Hola {nombre}, resumen de hoy: {stats[0]} nuevos encontrados, {stats[1]} listos para contactar."
                    self.enviar_notificacion(email, "Reporte Diario AutoNeura", cuerpo)
                    
        except Exception as e:
            logging.error(f"Error generando reportes: {e}")
        finally:
            cur.close()
            conn.close()

    # ==============================================================================
    # 🏁 BUCLE PRINCIPAL
    # ==============================================================================

    def iniciar_turno(self):
        logging.info(">>> 🤖 ORQUESTADOR SUPREMO (CON FRENO ANTI-429 Y PRESUPUESTO) 🤖 <<<")
        
        # --- HILOS PERMANENTES (DAEMONS) ---
        logging.info("🚀 Iniciando Hilo Permanente: TRABAJADOR ANALISTA")
        t_analista = threading.Thread(target=trabajar_analista, daemon=True)
        t_analista.start()

        logging.info("🚀 Iniciando Hilo Permanente: TRABAJADOR PERSUASOR")
        t_persuasor = threading.Thread(target=trabajar_persuasor, daemon=True)
        t_persuasor.start()

        ultima_revision_reportes = datetime.now() - timedelta(days=1)
        
        while True:
            try:
                inicio_ciclo = time.time()
                
                # 1. Gestión Financiera
                self.gestionar_finanzas_clientes()
                
                # 2. Operaciones Tácticas
                self.coordinar_operaciones_diarias()
                
                # 3. Reportes Diarios
                if datetime.now() > ultima_revision_reportes + timedelta(hours=24):
                    self.generar_reporte_diario()
                    ultima_revision_reportes = datetime.now()

                # 4. DESCANSO (10 Minutos)
                tiempo_ciclo = time.time() - inicio_ciclo
                logging.info(f"💤 Ciclo de coordinación finalizado en {tiempo_ciclo:.2f}s. Durmiendo 10 minutos...")
                time.sleep(600) 

            except KeyboardInterrupt:
                logging.info("🛑 Deteniendo sistema por orden del usuario...")
                break
            except Exception as e:
                logging.critical(f"🔥 ERROR CATASTRÓFICO EN MAIN LOOP: {e}")
                time.sleep(60)

if __name__ == "__main__":
    ceo = OrquestadorSupremo()
    ceo.iniciar_turno()
