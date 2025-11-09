import os
import json
import psycopg2
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIGURACIÓN ---
# Carga las variables de entorno (las mismas que usan los otros archivos)
load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Configura la IA de Google al iniciar
try:
    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
        print(">>> [Orquestador] IA de Google configurada.")
except Exception as e:
    print(f"!!! ERROR [Orquestador]: No se pudo configurar la IA de Google: {e}")


def analizar_orden_con_ia(orden_texto: str):
    """
    Usa la IA para analizar la orden de campaña y extraer la estrategia.
    """
    print(">>> [Orquestador] Fase 1: Enviando orden a la IA para análisis estratégico...")
    
    try:
        model = genai.GenerativeModel('models/gemini-pro-latest')
        
        # El prompt que le enseña a la IA a ser un estratega
        prompt = f"""
        Eres un estratega de marketing experto en prospección de clientes. Tu única tarea es analizar la siguiente orden de campaña y determinar la mejor estrategia de búsqueda.

        Debes extraer TRES datos clave:
        1.  `plataforma_objetivo`: ¿Cuál es la plataforma más lógica para encontrar a este tipo de cliente? Opciones válidas: "Google Maps", "Instagram", "TikTok", "Facebook", "LinkedIn".
        2.  `tipo_prospecto_objetivo`: ¿Qué estamos buscando? Opciones válidas: "Empresas", "Emprendedores", "Personas".
        3.  `palabra_clave_busqueda`: ¿Cuál es el término de búsqueda principal y conciso?

        Analiza esta orden:
        ---
        {orden_texto}
        ---

        Devuelve tu respuesta únicamente en formato JSON, sin texto adicional.
        """

        response = model.generate_content(prompt)
        
        # Limpiamos la respuesta para asegurarnos de que sea un JSON válido
        respuesta_json = response.text.replace("```json", "").replace("```", "").strip()
        
        estrategia = json.loads(respuesta_json)
        print(f">>> [Orquestador] Estrategia recibida de la IA: {estrategia}")
        return estrategia

    except Exception as e:
        print(f"!!! ERROR [Orquestador]: La IA falló al analizar la orden. Error: {e}")
        return None


def consultar_arsenal(estrategia: dict):
    """
    Usa la estrategia de la IA para encontrar la mejor herramienta en la base de datos.
    """
    plataforma = estrategia.get('plataforma_objetivo')
    tipo_prospecto = estrategia.get('tipo_prospecto_objetivo')
    
    print(f">>> [Orquestador] Fase 2: Consultando Arsenal en Supabase por la mejor herramienta para '{plataforma}' y '{tipo_prospecto}'...")
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # La consulta SQL inteligente que busca la mejor herramienta
        sql = """
            SELECT * FROM arsenal_herramientas 
            WHERE plataforma_objetivo = %s AND tipo_prospecto_objetivo = %s
            ORDER BY nivel_confianza DESC 
            LIMIT 1;
        """
        cur.execute(sql, (plataforma, tipo_prospecto))
        
        colnames = [desc[0] for desc in cur.description]
        fila = cur.fetchone()
        
        cur.close()
        conn.close()

        if fila:
            herramienta_elegida = dict(zip(colnames, fila))
            print(f">>> [Orquestador] ¡Herramienta seleccionada del Arsenal!: {herramienta_elegida.get('nombre_herramienta')}")
            return herramienta_elegida
        else:
            print(f"!!! ERROR [Orquestador]: No se encontró ninguna herramienta en el Arsenal para esa estrategia.")
            return None

    except Exception as e:
        print(f"!!! ERROR [Orquestador]: Falló la conexión con el Arsenal en Supabase. Error: {e}")
        if conn:
            conn.close()
        return None

# --- FUNCIÓN PRINCIPAL DEL ORQUESTADOR ---
def orquestar_nueva_caza(orden_campana: dict):
    """
    El flujo completo: recibe la orden, la analiza, consulta el arsenal y devuelve el plan de caza.
    """
    # 1. Construir un texto simple para que la IA lo analice
    texto_para_ia = (
        f"El cliente quiere una campaña llamada '{orden_campana.get('nombre_campana')}' "
        f"para vender '{orden_campana.get('que_vendes')}' "
        f"dirigido a '{orden_campana.get('a_quien_va_dirigido')}'."
    )

    # 2. Fase de Análisis IA
    estrategia_ia = analizar_orden_con_ia(texto_para_ia)
    if not estrategia_ia:
        return {"error": "La IA no pudo procesar la orden."}

    # 3. Fase de Consulta al Arsenal
    herramienta_optima = consultar_arsenal(estrategia_ia)
    if not herramienta_optima:
        return {"error": "No se encontraron herramientas para la estrategia definida por la IA."}
        
    # 4. Preparar la Orden Final para el Cazador
    orden_para_cazador = {
        "herramienta": herramienta_optima.get('nombre_herramienta'),
        "busqueda": estrategia_ia.get('palabra_clave_busqueda'),
        # En el futuro, la ubicación también la extraerá la IA
        "ubicacion": "Miami, Florida", 
        "max_resultados": int(orden_campana.get('prospectos_por_dia', 10))
    }
    
    print(f">>> [Orquestador] ¡Decisión tomada! Orden final para el Cazador: {orden_para_cazador}")
    return orden_para_cazador
