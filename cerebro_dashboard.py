import os
import google.generativeai as genai

print(">>> [Cerebro v2.0 - Recepcionista] Cargando...")

class DashboardBrain:
    # El constructor ahora ACEPTA la descripción del producto como un argumento
    def __init__(self, descripcion_producto: str):
        self.model = None
        self.chat = None

        # --- PROMPT DE SISTEMA - FASE 1: EL RECEPCIONISTA AMABLE ---
        protocolo_fase_1 = f"""
        ### ROL Y OBJETIVO ###
        Eres 'AutoNeura', un asistente de IA amigable y profesional. Tu objetivo principal es generar confianza y responder a las preguntas del cliente de forma clara y útil.

        ### BASE DE CONOCIMIENTO (Tu Negocio) ###
        La información del negocio que representas es la siguiente. Basa todas tus respuestas en esto:
        ---
        {descripcion_producto}
        ---

        ### PROTOCOLO DE CONVERSACIÓN ###
        1.  **Idioma:** Detecta el idioma del usuario y responde SIEMPRE en ese mismo idioma.
        2.  **Tono:** Mantén un tono servicial y positivo.
        3.  **Reciprocidad:** Siempre que sea posible, ofrece un dato útil o un consejo relacionado con la consulta del cliente antes de intentar vender.
        4.  **Validación:** Empieza tus respuestas validando la pregunta del cliente. Ej: "¡Excelente pregunta!", "Gracias por preguntar sobre...", "Entiendo que quieres saber más sobre...".
        """

        try:
            # Esta línea se queda intacta, usando el modelo correcto
            self.model = genai.GenerativeModel('models/gemini-pro-latest')
            
            # Iniciamos el chat inyectándole su nueva personalidad
            self.chat = self.model.start_chat(history=[
                {'role': 'user', 'parts': [protocolo_fase_1]},
                {'role': 'model', 'parts': ["Protocolo 'Recepcionista Amable' cargado. Estoy listo para ayudar y generar confianza."]}
            ])
            print(">>> [Cerebro] Conexión nativa con Google AI exitosa. Personalidad FASE 1 cargada.")
        except Exception as e:
            print(f"!!! ERROR [Cerebro]: No se pudo inicializar el modelo. {e} !!!")

    # LA FUNCIÓN INVOKE QUEDA 100% INTACTA, COMO PEDISTE
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

# La función ahora ACEPTA la descripción y se la PASA al cerebro
def create_chatbot(descripcion_producto: str):
    if not descripcion_producto:
        print("!!! WARNING [create_chatbot]: Se recibió una descripción vacía.")
        descripcion_producto = "un asistente genérico"

    brain_instance = DashboardBrain(descripcion_producto)
    if brain_instance.model:
        print(">>> [Cerebro] Instancia con personalidad creada exitosamente.")
        return brain_instance
    else:
        print("!!! ERROR [Cerebro]: La creación de la instancia falló.")
        return None
