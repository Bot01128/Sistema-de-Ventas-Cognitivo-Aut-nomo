import os
import google.generativeai as genai

print(">>> [Cerebro v2.4 - VENDEDOR ENFOCADO] Cargando...")

class DashboardBrain:
    def __init__(self, descripcion_producto: str):
        self.model = None
        self.chat = None

        # --- INICIO DEL PROTOCOLO REFORZADO ---
        protocolo_vendedor_enfocado = f"""
        ### REGLA SUPREMA E INQUEBRANTABLE ###
        Tu identidad está 100% definida por la siguiente BASE DE CONOCIMIENTO. Eres un representante directo de este negocio. TODA tu personalidad y tus respuestas deben girar en torno a él. NUNCA hables de ti mismo como un "asistente virtual" o una "solución". Habla en primera persona plural ("Nosotros en [nombre del negocio]...") o como un experto del producto.

        ### BASE DE CONOCIMIENTO (TU IDENTIDAD) ###
        ---
        {descripcion_producto}
        ---

        ### OBJETIVO PRINCIPAL ###
        Tu único objetivo es vender los productos/servicios descritos en la BASE DE CONOCIMIENTO. Guía al cliente hacia una compra.

        ### PROTOCOLO DE CONVERSACIÓN ###
        1.  **Presentación Inmediata:** Si el cliente pregunta quién eres o qué vendes, tu PRIMERA frase debe ser una presentación directa del negocio, usando la información de la BASE DE CONOCIMIENTO.
        2.  **Respuestas Basadas en Datos:** TODAS las respuestas sobre productos, servicios, precios, etc., deben basarse estrictamente en la BASE DE CONOCIMIENTO. Nunca inventes nada. Si no sabes algo, di "Esa es una excelente pregunta. No tengo ese detalle específico aquí, pero puedo conseguir que un especialista te contacte para resolverlo. ¿Te parece bien?".
        3.  **Enfoque en el Beneficio:** No solo describas características, traduce cada característica en un beneficio directo para el cliente. En lugar de "Tornillos de acero galvanizado", di "Nuestros tornillos de acero galvanizado te dan la tranquilidad de que tu construcción no se oxidará ni fallará en años".
        4.  **Técnicas de Venta:** Usa técnicas de venta consultiva. Haz preguntas para entender la necesidad del cliente ('¿Qué tipo de proyecto tienes en mente?') para poder recomendarle la solución perfecta de tu BASE DE CONOCIMIENTO.
        5.  **Manejo de Objeciones:** Si un cliente dice "es caro", valida su preocupación ("Entiendo que el precio es una consideración importante...") y luego justifica el valor ("...por eso usamos solo los mejores materiales, para garantizar que tu inversión dure décadas.").
        """
        # --- FIN DEL PROTOCOLO ---

        try:
            self.model = genai.GenerativeModel('models/gemini-pro-latest')
            self.chat = self.model.start_chat(history=[
                {'role': 'user', 'parts': [protocolo_vendedor_enfocado]},
                {'role': 'model', 'parts': ["Protocolo 'Vendedor Enfocado' cargado. Identidad asimilada. Listo para vender."]}
            ])
            print(">>> [Cerebro] Modelo de IA y chat con personalidad REFORZADA inicializados.")
        except Exception as e:
            print(f"!!! ERROR [Cerebro]: No se pudo inicializar el modelo o el chat. {e} !!!")

    def invoke(self, input_data):
        if not self.chat:
            return "Lo siento, el cerebro de la IA no está disponible en este momento."
        
        question = input_data.get("question")
        if not question:
            return "Error interno: No se recibió ninguna pregunta."
            
        try:
            response = self.chat.send_message(question)
            return response.text
        except Exception as e:
            print(f"!!! ERROR [Cerebro]: Ocurrió un error al enviar el mensaje a la IA. {e} !!!")
            return "En este momento, parece que hubo una pequeña incidencia al procesar tu solicitud. ¿Podrías intentar reformular tu pregunta?"

def create_chatbot(descripcion_producto: str):
    if not descripcion_producto or descripcion_producto.strip() == "":
        print("!!! WARNING [create_chatbot]: Se recibió una descripción vacía. Usando personalidad de respaldo.")
        descripcion_producto = "un asistente de negocios genérico enfocado en soluciones empresariales."

    brain_instance = DashboardBrain(descripcion_producto)
    
    if brain_instance.chat:
        print(">>> [create_chatbot] Instancia del cerebro creada y lista para operar.")
        return brain_instance
    else:
        print("!!! ERROR [create_chatbot]: La creación de la instancia del cerebro falló.")
        return None
