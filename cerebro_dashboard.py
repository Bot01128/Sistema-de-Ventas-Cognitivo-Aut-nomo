import os
import openai

print(">>> [Cerebro Dashboard v-OpenAI-Directo] Cargando...")

openai.api_key = os.environ.get("OPENAI_API_KEY")

PROMPT_SYSTEM = "Eres 'Auto', un asistente de IA amigable y ultra-eficiente, la cara visible de AutoNeura..."

def create_dashboard_brain():
    """
    Esta función ahora simplemente confirma que el modelo está listo.
    La lógica de la cadena se manejará directamente en main.py.
    """
    if not openai.api_key:
        print("!!! ADVERTENCIA [Cerebro v-OpenAI-Directo]: La clave de API de OpenAI no está disponible.")
        return None
    
    print(">>> [Cerebro Dashboard v-OpenAI-Directo] Creado exitosamente.")
    return openai # Devolvemos el cliente de OpenAI directamente
