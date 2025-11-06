import os
import google.generativeai as genai

print(">>> [Cerebro v-Nativo-Google] Cargando...")

# Esta clase manejará el estado de la conversación (la memoria)
class DashboardBrain:
    def __init__(self):
        self.model = None
        self.chat = None
        try:
            # Usamos el modelo que descubrimos que SÍ está disponible
            self.model = genai.GenerativeModel('models/gemini-pro-latest')
            
            # Iniciamos una sesión de chat para que recuerde el historial
            self.chat = self.model.start_chat(history=[])
            print(">>> [Cerebro] Conexión nativa con Google AI exitosa.")
        except Exception as e:
            print(f"!!! ERROR [Cerebro]: No se pudo inicializar el modelo de Google. {e} !!!")

    def invoke(self, input_data):
        if not self.chat:
            return "Error: El cerebro no está disponible en este momento."

        question = input_data.get("question")
        if not question:
            return "Error: No se recibió ninguna pregunta."

        try:
            response = self.chat.send_message(question)
            return response.text
        except Exception as e:
            print(f"!!! ERROR [Cerebro]: Ocurrió un error al invocar la IA. {e} !!!")
            return "Lo siento, tuve un problema para procesar tu solicitud."

# Esta es la función que main.py llamará
def create_chatbot():
    brain_instance = DashboardBrain()
    if brain_instance.model:
        print(">>> [Cerebro] Instancia creada exitosamente.")
        return brain_instance
    else:
        print("!!! ERROR [Cerebro]: La creación de la instancia falló.")
        return None
