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

# --- IMPORTACIÓN DE TUS EMPLEADOS (LOS TRABAJADORES) ---
try:
    # Asegúrate de que los nombres de archivo coincidan exactamente
    from trabajador_cazador import ejecutar_caza
    from trabajador_analista import TrabajadorAnalista
    from trabajador_persuasor import trabajar_persuasor
    from trabajador_nutridor import TrabajadorNutridor
    # Nota: Si el espía es crítico, impórtalo también:
    # from trabajador_espia import trabajar_espia 
except ImportError as e:
    print(f"!!! ERROR CRÍTICO DE INICIO: Faltan archivos de trabajadores. Detalle: {e}")
    # En producción no salimos, solo logueamos, pero para dev es mejor saberlo.
    # exit(1) 

# --- CONFIGURACIÓN ---
load_dotenv()

# Configuración de Logs (Guarda historial en archivo y muestra en consola)
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

# Cerebro Estratégico (Gemini)
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    modelo_estrategico = genai.GenerativeModel('gemini-1.5-flash')
else:
    logging.warning("⚠️ CEREBRO DESCONECTADO: No hay API Key de Google. El Orquestador será menos inteligente.")
    modelo_estrategico = None

class OrquestadorSupremo:
    def __init__(self):
        # Inicializamos a los jefes de departamento
        self.analista = TrabajadorAnalista()
        # Persuasor es una función, no clase en la última versión, pero lo manejamos en el método
        self.nutridor = TrabajadorNutridor()
        
    def conectar_db(self):
        return psycopg2.connect(DATABASE_URL)

    # ==============================================================================
    # 💰 DEPARTAMENTO FINANCIERO (COBROS Y SUSPENSIONES)
    # ==============================================================================

    def gestionar_finanzas_clientes(self):
        """
        Ciclo de facturación:
        1. Alerta preventiva (3 días antes).
        2. Intento de cobro (Día 0).
        3. Suspensión (Si falla).
        4. Eliminación (Si persiste mora).
        """
        logging.info("💼 Revisando estado de cuentas y pagos...")
        conn = self.conectar_db()
        cur = conn.cursor()
        
        try:
            # 1. ALERTA DE PAGO PRÓXIMO
            # Busca clientes activos que vencen en 3 días y no han sido avisados
            cur.execute("""
                SELECT id, email, full_name, next_payment_date 
                FROM clients 
                WHERE is_active = TRUE 
                AND next_payment_date BETWEEN NOW() AND NOW() + INTERVAL '3 DAYS'
                AND payment_alert_sent = FALSE
            """)
            por_vencer = cur.fetchall()
            for c in por_vencer:
                self.enviar_notificacion(c[1], "Tu suscripción vence pronto", f"Hola {c[2]}, recordatorio amistoso.")
                cur.execute("UPDATE clients SET payment_alert_sent = TRUE WHERE id = %s", (c[0],))

            # 2. PROCESAMIENTO DE COBROS (Día de Vencimiento)
            cur.execute("""
                SELECT id, email, balance, plan_cost 
                FROM clients 
                WHERE is_active = TRUE AND next_payment_date <= NOW()
            """)
            vencidos = cur.fetchall()
            
            for c in vencidos:
                cid, email, saldo, costo = c
                
                # LÓGICA DE COBRO (Simplificada: Saldo vs Costo)
                # Aquí podrías integrar Stripe/Cryptomus real para intentar cargar tarjeta
                if saldo >= costo:
                    nuevo_saldo = saldo - costo
                    cur.execute("""
                        UPDATE clients 
                        SET balance = %s, 
                            next_payment_date = next_payment_date + INTERVAL '30 DAYS', 
                            payment_alert_sent = FALSE 
                        WHERE id = %s
                    """, (nuevo_saldo, cid))
                    self.enviar_notificacion(email, "Pago Exitoso", "Tu servicio continúa sin interrupciones.")
                    logging.info(f"✅ Cobro exitoso: Cliente {cid}. Nuevo ciclo iniciado.")
                else:
                    # FALLO DE PAGO -> SUSPENSIÓN
                    cur.execute("UPDATE clients SET is_active = FALSE, status = 'suspended_payment_fail' WHERE id = %s", (cid,))
                    self.enviar_notificacion(email, "Servicio Suspendido", "No pudimos procesar tu pago. Tus bots se han detenido.")
                    logging.warning(f"⛔ Cliente {cid} suspendido por falta de fondos.")

            # 3. ELIMINACIÓN DE MOROSOS (La regla de los 2 días)
            # Si lleva 2 días suspendido y no pagó, se borra todo.
            cur.execute("""
                SELECT id, email FROM clients 
                WHERE status = 'suspended_payment_fail' 
                AND next_payment_date < NOW() - INTERVAL '2 DAYS'
            """)
            morosos = cur.fetchall()
            
            for m in morosos:
                cid, email = m
                logging.warning(f"🗑️ EJECUTANDO PROTOCOLO DE BORRADO para Cliente {cid}")
                
                # Borrado en cascada (primero hijos, luego padres)
                cur.execute("DELETE FROM prospects WHERE campana_id IN (SELECT id FROM campanas WHERE client_id = %s)", (cid,))
                cur.execute("DELETE FROM campanas WHERE client_id = %s", (cid,))
                # No borramos el cliente, lo marcamos como 'baja_definitiva' para historial
                cur.execute("UPDATE clients SET status = 'baja_definitiva', is_active = FALSE WHERE id = %s", (cid,))
                
                self.enviar_notificacion(email, "Cuenta Cancelada", "Tus datos han sido eliminados por falta de pago.")

            conn.commit()

        except Exception as e:
            logging.error(f"Error crítico en finanzas: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    # ==============================================================================
    # 🧠 DEPARTAMENTO DE ESTRATEGIA (LA IA PIENSA)
    # ==============================================================================

    def planificar_estrategia_caza(self, descripcion_producto, audiencia_objetivo):
        """
        Transforma "Vendo software" en -> "Buscar: Restaurantes nuevos en Miami"
        """
        if not modelo_estrategico:
            return audiencia_objetivo, "Google Maps" # Fallback tonto

        prompt = f"""
        Eres un Estratega de Marketing B2B.
        PRODUCTO: {descripcion_producto}
        AUDIENCIA DESEADA: {audiencia_objetivo}
        
        Tu tarea:
        1. Deduce quién es el comprador ideal REAL (no siempre es obvio).
        2. Genera una 'Query de Búsqueda' optimizada para encontrarlo en Google Maps.
        
        Responde SOLO con un JSON: {{"query": "...", "razonamiento": "..."}}
        """
        try:
            res = modelo_estrategico.generate_content(prompt)
            texto_json = res.text.strip().replace("```json", "").replace("```", "")
            data = json.loads(texto_json)
            return data.get("query", audiencia_objetivo), "Google Maps"
        except:
            return audiencia_objetivo, "Google Maps"

    # ==============================================================================
    # ⚙️ DEPARTAMENTO DE OPERACIONES (EJECUCIÓN DE TRABAJADORES)
    # ==============================================================================

    def ejecutar_trabajador_cazador_thread(self, cid, query, ubic, plat, cant):
        """Wrapper para correr el cazador en hilo independiente"""
        try:
            logging.info(f"🧵 Hilo de Caza iniciado para Campaña {cid}")
            ejecutar_caza(cid, query, ubic, plat, tipo_producto="Tangible", max_resultados=cant)
        except Exception as e:
            logging.error(f"Error en hilo de caza {cid}: {e}")

    def coordinar_operaciones_diarias(self):
        """
        El núcleo del sistema.
        1. Revisa si cumplimos la cuota de prospectos del día.
        2. Si falta, manda a CAZAR.
        3. Luego manda a ANALIZAR, PERSUADIR y NUTRIR en cadena.
        """
        conn = self.conectar_db()
        cur = conn.cursor()
        
        try:
            # A. OBTENER CAMPAÑAS ACTIVAS DE CLIENTES PAGADORES
            # Asumimos una tabla 'campanas' unida a 'clients'
            cur.execute("""
                SELECT c.id, c.nombre_campana, c.descripcion_producto, c.a_quien_va_dirigido, 
                       cl.prospects_limit_daily, c.geo_location
                FROM campanas c
                JOIN clients cl ON c.client_id = cl.id
                WHERE c.estado = 'activa' AND cl.is_active = TRUE
            """)
            campanas_activas = cur.fetchall()
            
            logging.info(f"⚙️ Coordinando {len(campanas_activas)} campañas activas...")

            for camp in campanas_activas:
                camp_id, nombre, prod, audiencia, cuota_diaria, ubicacion = camp
                
                # B. VERIFICAR PROGRESO DIARIO
                # Contamos cuántos se han cazado hoy para esta campaña
                cur.execute("""
                    SELECT COUNT(*) FROM prospects 
                    WHERE campana_id = %s 
                    AND created_at >= CURRENT_DATE
                """, (camp_id,))
                
                cazados_hoy = cur.fetchone()[0]
                
                # Regla de Sobrecaza (Factor 3x): 
                # Si el cliente paga por 4 leads válidos, cazamos 12 para tener margen de descarte.
                meta_caza = cuota_diaria * 3
                
                if cazados_hoy < meta_caza:
                    faltantes = meta_caza - cazados_hoy
                    
                    # 1. PENSAR (Estrategia)
                    query_optimizada, plataforma = self.planificar_estrategia_caza(prod, audiencia)
                    
                    logging.info(f"🚀 Ordenando Caza para '{nombre}'. Faltan {faltantes}. Query: '{query_optimizada}'")
                    
                    # 2. CAZAR (En paralelo para no bloquear)
                    t = threading.Thread(
                        target=self.ejecutar_trabajador_cazador_thread,
                        args=(camp_id, query_optimizada, ubicacion, plataforma, faltantes)
                    )
                    t.start()
                else:
                    logging.info(f"✅ Campaña '{nombre}' completa por hoy ({cazados_hoy}/{meta_caza}).")

            # C. PROCESAMIENTO EN CASCADA (Lotes)
            # Una vez lanzada la caza, procesamos lo que ya esté en la base de datos
            
            # 3. ESPÍA (Opcional, si tienes el archivo)
            # trabajar_espia() 

            # 4. ANALISTA
            logging.info("🕵️ Despertando al Analista...")
            self.analista.procesar_lote_prospectos(limite=10) # Procesa 10 por ciclo

            # 5. PERSUASOR
            logging.info("✍️ Despertando al Persuasor...")
            trabajar_persuasor(limite_lote=10)

            # 6. NUTRIDOR (Ajedrez)
            logging.info("♟️ Despertando al Nutridor...")
            self.nutridor.ejecutar_ciclo_seguimiento()

        except Exception as e:
            logging.error(f"Error en coordinación operaciones: {e}")
        finally:
            cur.close()
            conn.close()

    # ==============================================================================
    # 📨 COMUNICACIÓN Y REPORTES
    # ==============================================================================

    def enviar_notificacion(self, email, asunto, mensaje):
        """Wrapper para envío de emails (SendGrid, SMTP, etc.)"""
        # Aquí iría tu código de envío real. Por ahora logueamos.
        logging.info(f"📧 [SIMULACION EMAIL] A: {email} | Asunto: {asunto}")

    def generar_reporte_diario(self):
        """Genera y envía estadísticas a cada cliente"""
        conn = self.conectar_db()
        cur = conn.cursor()
        logging.info("📊 Generando reportes diarios...")
        
        try:
            cur.execute("SELECT id, email, full_name FROM clients WHERE is_active = TRUE")
            clientes = cur.fetchall()
            
            for c in clientes:
                cid, email, nombre = c
                
                # Estadísticas clave
                cur.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE estado_prospecto='cazado') as nuevos,
                        COUNT(*) FILTER (WHERE interacciones_nutridor >= 3) as calificados
                    FROM prospects p
                    JOIN campanas cam ON p.campana_id = cam.id
                    WHERE cam.client_id = %s 
                    AND p.created_at >= NOW() - INTERVAL '24 HOURS'
                """, (cid,))
                stats = cur.fetchone()
                
                if stats:
                    cuerpo = f"""
                    Hola {nombre}, resumen de hoy:
                    - Nuevos Prospectos Identificados: {stats[0]}
                    - Leads Calificados (Facturables): {stats[1]}
                    
                    El sistema sigue trabajando.
                    """
                    self.enviar_notificacion(email, "Reporte Diario AutoNeura", cuerpo)
                    
        finally:
            cur.close()
            conn.close()

    # ==============================================================================
    # 🏁 BUCLE PRINCIPAL (EL CORAZÓN DEL SISTEMA)
    # ==============================================================================

    def iniciar_turno(self):
        logging.info(">>> 🤖 ORQUESTADOR SUPREMO INICIADO 🤖 <<<")
        
        ultima_revision_reportes = datetime.now() - timedelta(days=1) # Para que corra pronto si hace falta
        
        while True:
            try:
                inicio_ciclo = time.time()
                
                # 1. GESTIÓN DE DINERO (Prioridad 1)
                self.gestionar_finanzas_clientes()
                
                # 2. OPERACIONES TÁCTICAS (Caza -> Venta)
                self.coordinar_operaciones_diarias()
                
                # 3. REPORTES (Una vez al día, ej: a las 8 AM o si pasó 24h)
                if datetime.now() > ultima_revision_reportes + timedelta(hours=24):
                    self.generar_reporte_diario()
                    ultima_revision_reportes = datetime.now()

                # 4. DESCANSO INTELIGENTE
                # No queremos fundir la base de datos haciendo queries cada milisegundo.
                # Un ciclo cada 10-15 minutos es saludable para un sistema de bots.
                tiempo_ciclo = time.time() - inicio_ciclo
                logging.info(f"💤 Ciclo finalizado en {tiempo_ciclo:.2f}s. Durmiendo 10 minutos...")
                time.sleep(600) 

            except KeyboardInterrupt:
                logging.info("🛑 Deteniendo sistema por orden del usuario...")
                break
            except Exception as e:
                logging.critical(f"🔥 ERROR CATASTRÓFICO EN MAIN LOOP: {e}")
                time.sleep(60) # Espera de seguridad antes de reiniciar

if __name__ == "__main__":
    ceo = OrquestadorSupremo()
    ceo.iniciar_turno()
