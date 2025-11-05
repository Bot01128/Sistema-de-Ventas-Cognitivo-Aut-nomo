import os
import requests
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
# --- YA NO IMPORTAMOS TAVILY ---

def run_follow_up():
    print("--- INICIANDO SCRIPT DE SEGUIMIENTO PROACTIVO ---")

    DATABASE_URL = os.environ.get("DATABASE_URL")
    PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
    
    if not DATABASE_URL or not PAGE_ACCESS_TOKEN:
        print("!!! ERROR CRÍTICO: Faltan variables de entorno. Abortando seguimiento. !!!")
        return

    # Usamos el modelo robusto de Google
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.7, api_version="v1")
    
    # --- SIMPLIFICAMOS EL PROMPT ---
    # Ya no necesitamos una búsqueda externa, la IA puede generar el contenido.
    follow_up_prompt = PromptTemplate.from_template("""Eres un asistente de AutoNeura AI. Tu misión es recontactar a un cliente que no ha respondido en más de 24 horas.
    Contexto de la última conversación:
    ---
    {conversation}
    ---
    Tu Tarea: Escribe un mensaje corto y amigable para reanudar la conversación. Aporta un nuevo dato de valor, una pregunta interesante o un beneficio que no se haya mencionado para reenganchar al usuario. Termina con un llamado a la acción suave.
    IMPORTANTE: Escribe en el mismo idioma de la conversación.
    Escribe solo el mensaje de seguimiento:""")

    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        try:
            # Crea la tabla de log si no existe
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS follow_up_log (
                    session_id VARCHAR(255) PRIMARY KEY,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
            connection.commit()

            # La lógica para encontrar sesiones inactivas se mantiene
            query = text("""
                SELECT session_id, MAX(created_at) as last_message_time
                FROM message_store -- Apuntamos a la nueva tabla de memoria
                WHERE session_id NOT IN (SELECT session_id FROM follow_up_log)
                GROUP BY session_id
                HAVING MAX(created_at) <= NOW() - INTERVAL '24 hours';
            """)
            inactive_sessions = connection.execute(query).fetchall()

            print(f"Se encontraron {len(inactive_sessions)} conversaciones inactivas.")

            for session in inactive_sessions:
                session_id = session[0]
                print(f"--- Procesando a: {session_id} ---")

                history_query = text("SELECT message FROM message_store WHERE session_id = :sid ORDER BY id DESC LIMIT 6")
                messages_raw = connection.execute(history_query, {"sid": session_id}).fetchall()
                # Adaptamos el formato del historial
                conversation_history = "\n".join([f"{msg[0]['type']}: {msg[0]['data']['content']}" for msg in reversed(messages_raw)])

                # Ya no necesitamos extraer el tema ni buscar en Tavily
                
                follow_up_chain = LLMChain(llm=llm, prompt=follow_up_prompt)
                message_to_send = follow_up_chain.invoke({"conversation": conversation_history})

                # La lógica de envío a Facebook se mantiene por ahora
                params = {"access_token": PAGE_ACCESS_TOKEN}
                headers = {"Content-Type": "application/json"}
                data = {"recipient": {"id": session_id}, "message": {"text": message_to_send}}
                r = requests.post("https://graph.facebook.com/v19.0/me/messages", params=params, headers=headers, json=data)
                
                if r.status_code == 200:
                    print(f"Mensaje enviado a {session_id}")
                    log_query = text("INSERT INTO follow_up_log (session_id) VALUES (:sid) ON CONFLICT (session_id) DO NOTHING;")
                    connection.execute(log_query, {"sid": session_id})
                    connection.commit()
                else:
                    print(f"!!! ERROR al enviar a {session_id}: {r.text}")
        
        except Exception as e:
            print(f"!!! ERROR GENERAL EN EL PROCESO DE SEGUIMIENTO: {e} !!!")
            connection.rollback()
            
    print("--- SCRIPT DE SEGUIMIENTO FINALIZADO ---")

if __name__ == "__main__":
    run_follow_up()
