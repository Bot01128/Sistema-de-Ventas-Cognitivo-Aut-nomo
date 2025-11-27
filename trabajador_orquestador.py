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
    # CAMBIO CRÍTICO: Usamos el modelo estable para evitar errores
    modelo_estrategico = genai.GenerativeModel('models/gemini-pro-latest')
else:
    logging.warning("⚠️ CEREBRO DESCONECTADO: No hay API Key de Google. El Orquestador será menos inteligente.")
    modelo_estrategico = None

class OrquestadorSupremo:
    def __init__(self):
        # Inicializamos a los jefes de departamento
        self.analista = TrabajadorAnalista()
        self.nutridor = TrabajadorNutridor()
        
    def conectar_db(self):
        return psycopg2.connect(DATABASE_URL)

    # ==============================================================================
    # 💰 MÓDULO 1: DEPARTAMENTO FINANCIERO (Garantiza que paguen)
    # ==============================================================================

    def gestionar_finanzas_clientes(self):
        """Revisa pagos, envía alertas y corta el servicio a morosos."""
        logging.info("💼 Revisando estado de cuentas y pagos...")
        conn = self.conectar_db()
        cur = conn.cursor()
        
        try:
            # 1. ALERTA DE PAGO PRÓXIMO (3 días antes)
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

            # 2. PROCESAMIENTO DE COBROS (El día del pago)
            cur.execute("""
                SELECT id, email, balance, plan_cost 
                FROM clients 
                WHERE is_active = TRUE AND next_payment_date <= NOW()
            """)
            for c in cur.fetchall():
                cid, email, saldo, costo = c or (0, "", 0, 0)
                costo = costo or 0
                
                if saldo and saldo >= costo:
                    # Cobro exitoso
                    nuevo_saldo = saldo - costo
                    cur.execute("""
                        UPDATE clients 
                        SET balance = %s, next_payment_date = next_payment_date + INTERVAL '30 DAYS', payment_alert_sent = FALSE 
                        WHERE id = %s
                    """, (nuevo_saldo, cid))
                    logging.info(f"✅ Cobro exitoso: Cliente {cid}. Nuevo ciclo iniciado.")
                elif costo > 0:
                    # Fallo de pago -> Suspensión
                    cur.execute("UPDATE clients SET is_active = FALSE, status = 'suspended_payment_fail' WHERE id = %s", (cid,))
                    self.enviar_notificacion(email, "Servicio Suspendido", "No tienes saldo suficiente. Recarga para continuar.")
                    logging.warning(f"⛔ Cliente {cid} suspendido por falta de fondos.")

            conn.commit()

        except Exception as e:
            logging.error(f"Error crítico en finanzas: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    # ==============================================================================
    # 🧠 MÓDULO 2: ESTRATEGIA DE MERCADO (IA decide qué buscar)
    # ==============================================================================

    def planificar_estrategia_caza(self, descripcion_producto, audiencia_objetivo, tipo_producto):
        """Define si buscar en Maps, TikTok o Instagram y qué palabra clave usar."""
        
        # Lógica de Rotación Básica
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
    # ⚙️ MÓDULO 3: COORDINACIÓN DE TRABAJADORES (Operaciones)
    # ==============================================================================

    def ejecutar_trabajador_cazador_thread(self, cid, query, ubic, plat, cant):
        """Lanza el Cazador en un hilo paralelo para no detener el sistema."""
        try:
            logging.info(f"🧵 Hilo de Caza iniciado para Campaña {cid} en {plat}")
            ejecutar_caza(cid, query, ubic, plat, tipo_producto="Variable", max_resultados=cant)
        except Exception as e:
            logging.error(f"Error en hilo de caza {cid}: {e}")

    def coordinar_operaciones_diarias(self):
        """Verifica metas diarias y activa a los trabajadores si faltan prospectos."""
        conn = self.conectar_db()
        cur = conn.cursor()
        
        try:
            # A. OBTENER CAMPAÑAS ACTIVAS (Tabla 'campaigns')
            cur.execute("""
                SELECT c.id, c.campaign_name, c.product_description, c.target_audience, 
                       c.product_type, cl.daily_prospects_quota, c.geo_location
                FROM campaigns c
                JOIN clients cl ON c.client_id = cl.id
                WHERE c.status = 'active' AND cl.is_active = TRUE
            """)
            campanas_activas = cur.fetchall()
            
            logging.info(f"⚙️ Coordinando {len(campanas_activas)} campañas activas...")

            for camp in campanas_activas:
                camp_id, nombre, prod, audiencia, tipo_prod, cuota_diaria, ubicacion = camp
                
                # B. VERIFICAR PROGRESO (Tabla 'prospects')
                cur.execute("""
                    SELECT COUNT(*) FROM prospects 
                    WHERE campaign_id = %s 
                    AND created_at::date = CURRENT_DATE
                """, (camp_id,))
                
                cazados_hoy = cur.fetchone()[0]
                
                # Regla de Sobrecaza (Factor 3x para asegurar calidad)
                meta_caza = (cuota_diaria or 4) * 3
                
                if cazados_hoy < meta_caza:
                    faltantes = meta_caza - cazados_hoy
                    
                    # 1. PENSAR (IA)
                    query_optimizada, plataforma = self.planificar_estrategia_caza(prod, audiencia, tipo_prod)
                    
                    logging.info(f"🚀 Ordenando Caza para '{nombre}'. Faltan {faltantes}. Query: '{query_optimizada}' en {plataforma}")
                    
                    # 2. CAZAR (Thread)
                    t = threading.Thread(
                        target=self.ejecutar_trabajador_cazador_thread,
                        args=(camp_id, query_optimizada, ubicacion, plataforma, faltantes)
                    )
                    t.start()
                    
                    # === FRENO DE MANO (MODIFICACIÓN VITAL) ===
                    logging.info("⏳ Pausando 10 segundos entre campañas para no saturar a Google...")
                    time.sleep(10)
                    
                else:
                    logging.info(f"✅ Campaña '{nombre}' completa por hoy ({cazados_hoy}/{meta_caza}).")

            # C. PROCESAMIENTO EN CASCADA (Analizar, Persuadir, Nutrir)
            
            logging.info("🕵️ Despertando al Analista...")
            self.analista.procesar_lote_prospectos(limite=10)

            logging.info("✍️ Despertando al Persuasor...")
            trabajar_persuasor(limite_lote=10)

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
                
                # CORRECCIÓN CRÍTICA: Usamos 'p.status'
                cur.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE p.status='cazado') as nuevos,
                        COUNT(*) FILTER (WHERE p.nurture_interactions_count >= 3) as calificados
                    FROM prospects p
                    JOIN campaigns cam ON p.campaign_id = cam.id
                    WHERE cam.client_id = %s 
                    AND p.created_at >= NOW() - INTERVAL '24 HOURS'
                """, (cid,))
                stats = cur.fetchone()
                
                if stats:
                    cuerpo = f"Hola {nombre}, resumen de hoy: {stats[0]} nuevos, {stats[1]} calificados."
                    self.enviar_notificacion(email, "Reporte Diario AutoNeura", cuerpo)
                    
        finally:
            cur.close()
            conn.close()

    # ==============================================================================
    # 🏁 BUCLE PRINCIPAL (EL CORAZÓN DEL SISTEMA)
    # ==============================================================================

    def iniciar_turno(self):
        logging.info(">>> 🤖 ORQUESTADOR SUPREMO (CON FRENO ANTI-429) 🤖 <<<")
        
        ultima_revision_reportes = datetime.now() - timedelta(days=1)
        
        while True:
            try:
                inicio_ciclo = time.time()
                
                # 1. Gestión Financiera
                self.gestionar_finanzas_clientes()
                
                # 2. Operaciones Tácticas (Caza -> Venta)
                self.coordinar_operaciones_diarias()
                
                # 3. Reportes Diarios
                if datetime.now() > ultima_revision_reportes + timedelta(hours=24):
                    self.generar_reporte_diario()
                    ultima_revision_reportes = datetime.now()

                # 4. DESCANSO INTELIGENTE (10 Minutos)
                tiempo_ciclo = time.time() - inicio_ciclo
                logging.info(f"💤 Ciclo finalizado en {tiempo_ciclo:.2f}s. Durmiendo 10 minutos...")
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