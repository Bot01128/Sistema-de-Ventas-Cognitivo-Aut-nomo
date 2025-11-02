import os
# ¡NUEVAS IMPORTACIONES PARA GOOGLE!
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

print(">>> [Cerebro Dashboard v-Google] Cargando...")

try:
    # ¡CAMBIAMOS EL MOTOR DE IA A GOOGLE GEMINI!
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.7)
    print(">>> [Cerebro Dashboard v-Google] Conexión con Google AI exitosa.")
except Exception as e:
    print(f"!!! ERROR [Cerebro v-Google]: No se pudo inicializar. Revisa tu GOOGLE_API_KEY. Error: {e} !!!")
    llm = None

# Mantenemos y mejoramos el prompt
PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Eres 'Auto', un asistente de IA amigable y ultra-eficiente, la cara visible de AutoNeura. Tu propósito es responder a las preguntas de los clientes sobre los planes, características y funcionamiento del sistema de ventas automatizado. Tu tono debe ser claro, servicial y generar confianza. No eres el sistema que busca prospectos, eres el asistente que ayuda al usuario en el dashboard."),
    ("human", "{question}"),
])

def create_dashboard_brain():
    """
    Crea y devuelve la cadena de LangChain para el chat del dashboard.
    """
    if not llm:
        print("!!! ADVERTENCIA [Cerebro v-Google]: El modelo de IA no está disponible. El chat no funcionará.")
        return None
    
    chain = PROMPT | llm | StrOutputParser()
    print(">>> [Cerebro Dashboard v-Google] Creado exitosamente.")
    return chain
