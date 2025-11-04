import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_message_histories import PostgresChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

print(">>> [Cerebro] Cargando...")
llm = None
try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.7, api_version="v1")
    print(">>> [Cerebro] Conexión con Google AI (v1) exitosa.")
except Exception as e:
    print(f"!!! ERROR [Cerebro]: {e} !!!")

PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Eres 'Auto', un asistente de IA amigable..."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
])

def get_chat_history(session_id: str):
    db_url = os.environ.get("DATABASE_URL")
    return PostgresChatMessageHistory(
        session_id=session_id,
        connection_string=db_url,
        table_name="message_store"
    )

def create_chatbot():
    if not llm: return None
    chain = PROMPT | llm
    chatbot_with_history = RunnableWithMessageHistory(
        chain,
        get_chat_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    print(">>> [Cerebro] Creado exitosamente.")
    return chatbot_with_history
