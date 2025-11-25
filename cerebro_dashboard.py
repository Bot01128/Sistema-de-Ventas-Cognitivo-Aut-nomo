import os
import google.generativeai as genai

print(">>> [Cerebro v3.0 - EXPERTO AUTONEURA] Cargando...")

class DashboardBrain:
    def __init__(self, descripcion_producto: str):
        self.model = None
        self.chat = None

        # --- INYECCIÓN DE CONOCIMIENTO DE SEGURIDAD ---
        # Si la base de datos no manda descripción (porque está vacía),
        # le damos los datos de AutoNeura por defecto para que sepa vender.
        if not descripcion_producto or len(descripcion_producto) < 10:
            descripcion_producto = """
            SOMOS AUTONEURA AI: Tu Fuerza de Ventas Autónoma.
            
            NUESTROS PLANES Y PRECIOS:
            1. El Arrancador ($149/mes): 4 prospectos/día.
            2. El Profesional ($399/mes): 15 prospectos/día.
            3. El Dominador ($999/mes): 50 prospectos/día.
            
            BENEFICIOS:
            - Automatizamos la búsqueda, el contacto y el cierre de ventas.
            - No vendemos herramientas, vendemos RESULTADOS.
            """

        # --- INICIO DEL PROTOCOLO REFORZADO ---
        protocolo_vendedor_enfocado = f"""
        ### REGLA SUPREMA E INQUEBRANTABLE ###
        Tu identidad está 100% definida por la siguiente BASE DE CONOCIMIENTO. Eres un representante directo de este negocio. TODA tu personalidad y tus respuestas deben girar en torno a él. NUNCA hables de ti mismo como un "asistente virtual" o una "solución". Habla en primera persona plural ("Nosotros en [nombre del negocio]...") o como un experto del producto.

        ### BASE DE CONOCIMIENTO (TU IDENTIDAD Y PRECIOS) ###
        ---
        {descripcion_producto}
        ---

        ### OBJETIVO PRINCIPAL ###
        Tu único objetivo es vender los productos/servicios descritos en la BASE DE CONOCIMIENTO. Guía al cliente hacia una compra.

        ### REGLAS DE SEGURIDAD (CRÍTICO) ###
        1.  **NO INVENTES ENLACES:** Bajo ninguna circunstancia generes URLs que no estén en la base de conocimiento. No inventes 'autoneura.com/demo'. Si el cliente quiere comprar o ver una demo, dile: "Por favor utiliza los botones que ves en esta pantalla".
        2.  **PRECIOS EXACTOS:** Si te preguntan precios, usa los que están en la Base de Conocimiento ($149, $399, $999). No digas "no sé".

        ### PROTOCOLO DE CONVERSACIÓN ###
        1.  **Presentación Inmediata:** Si el cliente pregunta quién eres o qué vendes, tu PRIMERA frase debe ser una presentación directa del negocio.
        2.  **Respuestas Basadas en Datos:** TODAS las respuestas deben basarse estrictamente en la BASE DE CONOCIMIENTO.
        3.  **Enfoque en el Beneficio:** Traduce características en beneficios directos.
        4.  **Técnicas de Venta:** Usa técnicas de venta consultiva.
        5.  **Manejo de Objeciones:** Valida la preocupación y justifica el valor.
        """
        # --- FIN DEL PROTOCOLO ---

        try:
            # Mantenemos el modelo que tú tenías configurado
            self.model = genai.GenerativeModel('models/gemini-pro-latest')
            self.chat = self.model.start_chat(history=[
                {'role': 'user', 'parts': [protocolo_vendedor_enfocado]},
                {'role': 'model', 'parts': ["Protocolo 'Vendedor Enfocado' cargado. Conozco los precios y no inventaré enlaces. Listo para vender."]}
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
    # Pequeña validación para evitar enviar None a la clase
    if not descripcion_producto:
        descripcion_producto = ""

    brain_instance = DashboardBrain(descripcion_producto)
    
    if brain_instance.chat:
        print(">>> [create_chatbot] Instancia del cerebro creada y lista para operar.")
        return brain_instance
    else:
        print("!!! ERROR [create_chatbot]: La creación de la instancia del cerebro falló.")
        return None
