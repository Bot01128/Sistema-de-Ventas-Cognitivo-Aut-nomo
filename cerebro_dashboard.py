import os
import google.generativeai as genai
import psycopg2

print(">>> [Cerebro Dashboard v-Google-Directo] Cargando...")

model = None
try:
    # La GOOGLE_API_KEY ya debería estar configurada en el main.py
    # Aquí solo intentamos inicializar el modelo.
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    print(">>> [Cerebro Dashboard v-Google-Directo] Modelo de IA inicializado.")
except Exception as e:
    print(f"!!! ERROR [Cerebro v-Google-Directo]: {e} !!!")

# El prompt ahora es un texto simple, no un objeto complejo.
PROMPT_SYSTEM = "Eres 'Auto', un asistente de IA amigable y ultra-eficiente, la cara visible de AutoNeura..."

def get_chat_history(session_id: str):
    db_url = os.environ.get("DATABASE_URL")
    # ... (Aquí iría la lógica para obtener el historial de la base de datos) ...
    return [] # Por ahora, devolvemos una lista vacía

def save_chat_history(session_id: str, message: dict):
    db_url = os.environ.get("DATABASE_URL")
    # ... (Aquí iría la lógica para guardar el mensaje en la base de datos) ...
    pass

def create_dashboard_brain():
    """
    Esta función ahora simplemente confirma que el modelo está listo.
    La lógica de la cadena se manejará directamente en main.py.
    """
    if not model:
        print("!!! ADVERTENCIA [Cerebro v-Google-Directo]: El modelo de IA no está disponible.")
        return None
    
    print(">>> [Cerebro Dashboard v-Google-Directo] Creado exitosamente.")
    return model # Devolvemos el modelo directamente
