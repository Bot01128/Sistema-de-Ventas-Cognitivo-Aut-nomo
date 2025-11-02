import os
import google.generativeai as genai

print(">>> [Cerebro v-Google] Cargando...")

# Variable global para el modelo
MODELO_GEMINI = None
PROMPT_SISTEMA = "Eres 'Auto', un asistente de IA amigable y ultra-eficiente..."

try:
    # No configuramos la clave aquí, solo inicializamos el modelo.
    # main.py se encargará de la configuración.
    MODELO_GEMINI = genai.GenerativeModel('gemini-1.5-flash-latest')
    print(">>> [Cerebro v-Google] Modelo de IA listo.")
except Exception as e:
    print(f"!!! ERROR [Cerebro v-Google]: {e} !!!")

def obtener_cerebro():
    # Esta función simplemente devuelve el modelo ya inicializado.
    return MODELO_GEMINI

def obtener_prompt_sistema():
    return PROMPT_SISTEMA
