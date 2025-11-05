import os
import google.generativeai as genai
import psycopg2
import json

print(">>> [Cerebro v-Google-Directo-CON-MEMORIA] Cargando...")

model = None
try:
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    print(">>> [Cerebro] Modelo de IA inicializado.")
except Exception as e:
    print(f"!!! ERROR [Cerebro]: {e} !!!")

PROMPT_SYSTEM = "Eres 'Auto', un asistente de IA amigable..."

def get_chat_history(session_id: str):
    db_url = os.environ.get("DATABASE_URL")
    history = []
    conn = None
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("SELECT message FROM message_store WHERE session_id = %s ORDER BY id ASC", (session_id,))
        rows = cur.fetchall()
        for row in rows:
            history.append(json.loads(row[0]))
    except Exception as e:
        print(f"!!! ERROR al obtener historial de chat: {e} !!!")
    finally:
        if conn:
            cur.close()
            conn.close()
    
    formatted_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    return formatted_history

def save_chat_history(session_id: str, message: dict):
    db_url = os.environ.get("DATABASE_URL")
    conn = None
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("INSERT INTO message_store (session_id, message) VALUES (%s, %s)", (session_id, json.dumps(message)))
        conn.commit()
    except Exception as e:
        print(f"!!! ERROR al guardar historial de chat: {e} !!!")
    finally:
        if conn:
            cur.close()
            conn.close()
