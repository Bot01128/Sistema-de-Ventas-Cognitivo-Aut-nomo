import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain

# --- INICIALIZACIÓN DEL MODELO DE LENGUAJE ---
try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.5)
    print(">>> [Cerebro Dashboard] Conexión con Google AI exitosa.")
except Exception as e:
    print(f"!!! ERROR [Cerebro Dashboard]: No se pudo conectar a Google AI: {e} !!!")
    llm = None

# --- INSTRUCCIONES PARA EL ASISTENTE DEL DASHBOARD ---
prompt_template = """
Eres 'Auto', un asistente de IA amigable y ultra-eficiente para la plataforma 'AutoNeura AI'.
Tu misión es ayudar a los usuarios a configurar sus campañas de prospección.
Habla de forma concisa y directa. Guía al usuario paso a paso.
Si el usuario te pregunta cómo hacer algo, explícaselo de forma simple.
Si el usuario te pide que inicies una campaña, extráe la información clave (tipo de negocio, ubicación) y confírmala.

Historial de conversación:
{chat_history}

Pregunta del Usuario: {question}
Tu Respuesta:
"""

PROMPT = ChatPromptTemplate.from_template(prompt_template)

# --- MEMORIA DE LA CONVERSACIÓN ---
# Usamos una memoria simple que se reiniciará si el servidor se reinicia.
# Más adelante la conectaremos a una base de datos.
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# --- FUNCIÓN PRINCIPAL DE CREACIÓN DEL CEREBRO ---
def create_dashboard_brain():
    if not llm:
        return None
    
    # Creamos la "cadena" que une el Prompt, el Modelo de IA y la Memoria
    brain_chain = LLMChain(
        llm=llm,
        prompt=PROMPT,
        memory=memory,
        verbose=True # Imprimirá en los logs lo que está pensando
    )
    print(">>> [Cerebro Dashboard] Creado exitosamente.")
    return brain_chain
