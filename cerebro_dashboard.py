import os
import google.generativeai as genai

print(">>> [Cerebro Dashboard v-Google-Directo] Cargando...")

model = None
try:
    # La GOOGLE_API_KEY ya debería estar configurada en el main.py
    # Aquí solo intentamos inicializar el modelo.
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    print(">>> [Cerebro Dashboard v-Google-Directo] Modelo de IA inicializado.")
except Exception as e:
    print(f"!!! ERROR [Cerebro v-Google-Directo]: {e} !!!")

PROMPT_SYSTEM = "Eres 'Auto', un asistente de IA amigable y ultra-eficiente, la cara visible de AutoNeura..."
