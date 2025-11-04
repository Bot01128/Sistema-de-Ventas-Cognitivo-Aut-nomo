import os
from flask import Flask, request
from dotenv import load_dotenv
from twilio.rest import Client
from cerebro import create_chatbot

print(">>> [main.py] Cargando Módulo... VERSIÓN BACKEND-PURO")
load_dotenv()
app = Flask(__name__)
print(">>> [main.py] App Flask creada.")

# --- CONFIGURACIÓN DE TWILIO ---
try:
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_FACEBOOK_SENDER_ID = os.environ.get('TWILIO_FACEBOOK_SENDER_ID')
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    print(">>> [main.py] Cliente Twilio inicializado.")
except Exception as e:
    print(f"!!! ERROR [main.py]: Faltan las credenciales de Twilio o son incorrectas: {e} !!!")
    twilio_client = None

# --- INICIALIZACIÓN DEL CEREBRO ---
final_chain = create_chatbot()

# --- RUTA PRINCIPAL (PARA VERIFICAR QUE ESTÁ VIVO) ---
@app.route('/')
def home():
    # Este es el mensaje simple que debe mostrar la URL pública
    return "<h1>Servidor AutoNeura AI (Twilio) está VIVO</h1>", 200

# --- RUTA WEBHOOK PARA TWILIO ---
@app.route('/webhook', methods=['POST'])
def webhook():
    if not twilio_client or not final_chain:
        print("!!! ERROR CRÍTICO [main.py]: El bot no está configurado correctamente. Ignorando mensaje.")
        return "OK", 200

    incoming_data = request.values
    sender_id = incoming_data.get('From')
    message_text = incoming_data.get('Body')
    
    if sender_id and sender_id.startswith('messenger:'):
        sender_id = sender_id.replace('messenger:', '')

    if sender_id and message_text:
        print(f"--- [BACKEND-PURO] Mensaje de {sender_id}: '{message_text}' ---")
        try:
            response_object = final_chain.invoke(
                {"input": message_text},
                config={"configurable": {"session_id": sender_id}}
            )
            response_text = response_object.content
            
            print(f"--- [BACKEND-PURO] Respuesta IA: '{response_text}' ---")
            send_message_via_twilio(sender_id, response_text)
        except Exception as e:
            print(f"!!! ERROR [BACKEND-PURO] al procesar mensaje: {e} !!!")
    
    return "OK", 200

# --- FUNCIÓN PARA ENVIAR MENSAJES VÍA TWILIO ---
def send_message_via_twilio(recipient_id, message_text):
    try:
        message = twilio_client.messages.create(
            to=f'messenger:{recipient_id}',
            from_=f'messenger:{TWILIO_FACEBOOK_SENDER_ID}',
            body=message_text
        )
        print(f"Mensaje [BACKEND-PURO] enviado SID: {message.sid}")
    except Exception as e:
        print(f"!!! ERROR [BACKEND-PURO] al enviar con Twilio: {e} !!!")

print(">>> [main.py] Módulo cargado. VERSIÓN BACKEND-PURO")
