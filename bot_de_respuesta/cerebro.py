import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_message_histories import PostgresChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

print(">>> [cerebro.py] Cargando Módulo... VERSIÓN COMMUNITY CORREGIDA")

llm = None
try:
    # --- LA SOLUCIÓN DEFINITIVA BASADA EN LA INVESTIGACIÓN ---
    # Usamos el modelo más robusto y forzamos la API a la versión estable 'v1'
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.7, api_version="v1")
    print(">>> [cerebro.py] Conexión con Google AI (v1) exitosa.")
except Exception as e:
    print(f"!!! ERROR [cerebro.py]: No se pudo conectar a Google AI: {e} !!!")
    llm = None

def get_chat_history(session_id: str):
    """
    Obtiene el historial de chat para una sesión específica desde la base de datos Postgres.
    """
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("!!! ERROR CRÍTICO [cerebro.py]: La variable de entorno DATABASE_URL no está configurada.")
        # Devolvemos un historial en memoria para que no crashee, pero no recordará nada.
        from langchain_core.chat_history import InMemoryChatMessageHistory
        return InMemoryChatMessageHistory()
        
    return PostgresChatMessageHistory(
        session_id=session_id,
        connection_string=db_url,
        table_name="message_store"
    )

# Este es el prompt que el cliente podrá modificar en el futuro
PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Eres 'Auto', un asistente de IA amigable y ultra-eficiente, la cara visible de AutoNeura. Tu propósito es responder a las preguntas de los clientes sobre los planes, características y funcionamiento del sistema de ventas automatizado. Tu tono debe ser claro, servicial y generar confianza."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
])

def create_chatbot():
    """
    Crea la cadena de LangChain completa, con memoria.
    """
    if not llm:
        return None
    try:
        chain = PROMPT | llm
        
        chatbot_with_history = RunnableWithMessageHistory(
            chain,
            get_chat_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )
        print(">>> [cerebro.py] Cerebro con memoria creado exitosamente.")
        return chatbot_with_history
    except Exception as e:
        print(f"!!! ERROR [cerebro.py] al crear la cadena de LangChain: {e} !!!")
        return None

print(">>> [cerebro.py] Módulo cargado.")
