import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

print(">>> [Cerebro Dashboard v3 - Simple] Cargando...")

try:
    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.5)
    print(">>> [Cerebro Dashboard v3] Conexión con Google AI exitosa.")
except Exception as e:
    print(f"!!! ERROR [Cerebro v3]: {e} !!!")
    llm = None

PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Eres 'Auto', un asistente de IA amigable y ultra-eficiente..."),
    ("human", "{question}"),
])

def create_dashboard_brain():
    if not llm:
        return None
    
    # Sintaxis moderna, simple y sin memoria (por ahora)
    chain = PROMPT | llm | StrOutputParser()
    print(">>> [Cerebro Dashboard v3] Creado exitosamente.")
    return chain
