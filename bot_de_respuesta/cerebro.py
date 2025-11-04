import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_message_histories import PostgresChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

print(">>> [Cerebro Trasplantado] Cargando Módulo...")

# --- CARGA DE LA BASE DE CONOCIMIENTO ---
knowledge_base = ""
try:
    # La ruta ahora es relativa a la raíz del proyecto principal
    with open("bot_de_respuesta/database.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
    print(">>> [Cerebro Trasplantado] Base de conocimiento cargada exitosamente.")
except FileNotFoundError:
    print("!!! ADVERTENCIA [Cerebro Trasplantado]: No se encontró el archivo database.txt.")
except Exception as e:
    print(f"!!! ERROR [Cerebro Trasplantado] al leer database.txt: {e} !!!")


llm = None
try:
    # Usamos el modelo robusto y la API estable
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.7, api_version="v1")
    print(">>> [Cerebro Trasplantado] Conexión con Google AI (v1) exitosa.")
except Exception as e:
    print(f"!!! ERROR [Cerebro Trasplantado]: No se pudo conectar a Google AI: {e} !!!")
    llm = None

def get_chat_history(session_id: str):
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("!!! ERROR CRÍTICO [Cerebro Trasplantado]: DATABASE_URL no configurada.")
        from langchain_core.chat_history import InMemoryChatMessageHistory
        return InMemoryChatMessageHistory()
    return PostgresChatMessageHistory(
        session_id=session_id,
        connection_string=db_url,
        table_name="message_store"
    )

# --- PROMPT MEJORADO CON BASE DE CONOCIMIENTO ---
PROMPT = ChatPromptTemplate.from_messages([
    ("system", f"""Eres 'Auto', un asistente de ventas experto para 'Ferretería El Tornillo Feliz'. Tu única misión es responder las preguntas de los clientes basándote ESTRICTAMENTE en la siguiente información de la empresa. No inventes nada. Si no sabes la respuesta, di "No tengo esa información, pero puedo contactarte con un representante humano".

    --- BASE DE CONOCIMIENTO ---
    {knowledge_base}
    ---------------------------
    """),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
])

def create_chatbot():
    if not llm: return None
    try:
        chain = PROMPT | llm
        chatbot_with_history = RunnableWithMessageHistory(
            chain,
            get_chat_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )
        print(">>> [Cerebro Trasplantado] Cerebro con memoria y conocimiento creado.")
        return chatbot_with_history
    except Exception as e:
        print(f"!!! ERROR [Cerebro Trasplantado] al crear la cadena: {e} !!!")
        return None

print(">>> [Cerebro Trasplantado] Módulo cargado.")
