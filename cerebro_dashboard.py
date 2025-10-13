import os
# ¡NUEVAS IMPORTACIONES!
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

print(">>> [Cerebro Dashboard v-OpenAI] Cargando...")

try:
    # ¡CAMBIAMOS EL MOTOR DE IA!
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)
    print(">>> [Cerebro Dashboard v-OpenAI] Conexión con OpenAI exitosa.")
except Exception as e:
    print(f"!!! ERROR [Cerebro v-OpenAI]: {e} !!!")
    llm = None

PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Eres 'Auto', un asistente de IA amigable y ultra-eficiente..."),
    ("human", "{question}"),
])

def create_dashboard_brain():
    if not llm:
        return None
    
    chain = PROMPT | llm | StrOutputParser()
    print(">>> [Cerebro Dashboard v-OpenAI] Creado exitosamente.")
    return chain
