import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

print(">>> [Cerebro Dashboard v4 - Modelo Básico] Cargando...")

try:
    # --- ¡ESTE ES EL ÚNICO CAMBIO! ---
    # Usamos un modelo más antiguo y básico que es más probable que
    # esté disponible para todas las claves de API.
    llm = ChatGoogleGenerativeAI(model="gemini-1.0-pro", temperature=0.5)
    print(">>> [Cerebro Dashboard v4] Conexión con Google AI exitosa.")
except Exception as e:
    print(f"!!! ERROR [Cerebro v4]: {e} !!!")
    llm = None

PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Eres 'Auto', un asistente de IA amigable y ultra-eficiente. Tu objetivo es ayudar a los usuarios a configurar campañas de prospección. Eres conciso y vas al grano."),
    ("human", "{question}"),
])

def create_dashboard_brain():
    if not llm:
        return None
    
    # Sintaxis moderna, simple y sin memoria (por ahora)
    chain = PROMPT | llm | StrOutputParser()
    print(">>> [Cerebro Dashboard v4] Creado exitosamente.")
    return chain
