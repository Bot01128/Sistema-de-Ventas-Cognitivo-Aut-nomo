import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.5)
    print(">>> [Cerebro Dashboard v2] Conexión con Google AI exitosa.")
except Exception as e:
    print(f"!!! ERROR [Cerebro Dashboard v2]: No se pudo conectar a Google AI: {e} !!!")
    llm = None

PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Eres 'Auto', un asistente de IA amigable y ultra-eficiente..."),
    ("human", "{question}"),
])

def create_dashboard_brain():
    if not llm:
        return None
    
    # Sintaxis moderna con LCEL, sin LLMChain
    chain = PROMPT | llm | StrOutputParser()
    print(">>> [Cerebro Dashboard v2] Creado exitosamente.")
    return chain
