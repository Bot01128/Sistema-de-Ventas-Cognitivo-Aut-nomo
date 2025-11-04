import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

print(">>> [Cerebro] Cargando...")
llm = None
try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.7, api_version="v1")
    print(">>> [Cerebro] Conexión con Google AI (v1) exitosa.")
except Exception as e:
    print(f"!!! ERROR [Cerebro]: {e} !!!")

PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Eres 'Auto', un asistente de IA amigable..."),
    ("human", "{question}"),
])

def create_dashboard_brain():
    if not llm: return None
    chain = PROMPT | llm | StrOutputParser()
    print(">>> [Cerebro] Creado exitosamente.")
    return chain
