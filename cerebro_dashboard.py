import os
# ¡Importaciones correctas para LangChain + Google!
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

print(">>> [Cerebro Dashboard v-LangChain-Google] Cargando...")

try:
    # --- ¡LA SOLUCIÓN DE LOS FOROS! ---
    # Usamos LangChain, pero forzamos la versión de la API a 'v1'
    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7, api_version="v1")
    print(">>> [Cerebro Dashboard v-LangChain-Google] Conexión con Google AI (v1) exitosa.")
except Exception as e:
    print(f"!!! ERROR [Cerebro v-LangChain-Google]: {e} !!!")
    llm = None

# Mantenemos el prompt profesional de LangChain
PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Eres 'Auto', un asistente de IA amigable y ultra-eficiente, la cara visible de AutoNeura. Tu propósito es responder a las preguntas de los clientes sobre los planes, características y funcionamiento del sistema de ventas automatizado. Tu tono debe ser claro, servicial y generar confianza."),
    ("human", "{question}"),
])

def create_dashboard_brain():
    """
    Crea y devuelve la cadena de LangChain para el chat del dashboard.
    """
    if not llm:
        print("!!! ADVERTENCIA [Cerebro v-LangChain-Google]: El modelo de IA no está disponible.")
        return None
    
    # La cadena sigue siendo la misma: Prompt -> LLM -> Parser
    chain = PROMPT | llm | StrOutputParser()
    print(">>> [Cerebro Dashboard v-LangChain-Google] Creado exitosamente.")
    return chain
