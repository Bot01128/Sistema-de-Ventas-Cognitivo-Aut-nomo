import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

print(">>> [Cerebro Dashboard v-LangChain-Google-Corregido] Cargando...")

llm = None
try:
    # --- LA BALA DE PLATA DEFINITIVA ---
    # Usamos LangChain, con el modelo más nuevo y forzando la API a 'v1'.
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.7, api_version="v1")
    print(">>> [Cerebro Dashboard v-LangChain-Google-Corregido] Conexión con Google AI (v1) exitosa.")
except Exception as e:
    print(f"!!! ERROR [Cerebro v-LangChain-Google-Corregido]: {e} !!!")
    # Este error puede ocurrir si GOOGLE_API_KEY no está bien configurada en los Secrets.
    
# El prompt profesional que ya teníamos
PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Eres 'Auto', un asistente de IA amigable y ultra-eficiente, la cara visible de AutoNeura. Tu propósito es responder a las preguntas de los clientes sobre los planes, características y funcionamiento del sistema de ventas automatizado. Tu tono debe ser claro, servicial y generar confianza."),
    ("human", "{question}"),
])

# Dejamos la función create_dashboard_brain como la teníamos, porque es la correcta
def create_dashboard_brain():
    """
    Crea y devuelve la cadena de LangChain para el chat del dashboard.
    """
    if not llm:
        print("!!! ADVERTENCIA [Cerebro v-LangChain-Google-Corregido]: El modelo de IA no está disponible.")
        return None
    
    # La cadena sigue siendo la misma: Prompt -> LLM -> Parser de Texto
    chain = PROMPT | llm | StrOutputParser()
    print(">>> [Cerebro Dashboard v-LangChain-Google-Corregido] Creado exitosamente.")
    return chain
