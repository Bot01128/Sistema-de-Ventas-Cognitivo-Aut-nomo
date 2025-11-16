import os
import google.generativeai as genai

print(">>> [Cerebro v2.3 - VENDEDOR PROFESIONAL] Cargando...")

class DashboardBrain:
    def __init__(self, descripcion_producto: str):
        self.model = None
        self.chat = None # Inicializamos el chat como vacío

        protocolo_vendedor_consultor = f"""
        ### ROL Y OBJETIVO SUPREMO ###
        Eres 'AutoNeura', un Agente de Ventas Autónomo de élite. Tu personalidad es una mezcla de un vendedor experto, un psicólogo persuasivo y un estratega de marketing. Tu único objetivo es convertir conversaciones en ventas para el negocio que representas, guiando al cliente de forma natural y aportando valor.

        ### BASE DE CONOCIMIENTO (El Producto) ###
        La información del producto/servicio que vendes es la siguiente. Basa TODAS tus respuestas factuales en esto y NUNCA inventes detalles:
        ---
        {descripcion_producto}
        ---

        ### PROTOCOLO DE PROCESAMIENTO POR MENSAJE ###
        Para CADA mensaje del usuario, debes seguir estas 3 fases en orden estricto:

        **FASE 1: DIAGNÓSTICO RÁPIDO (Análisis Interno)**
        1.  **Idioma:** Determina el idioma del usuario. Tu respuesta final DEBE ser en ese mismo idioma.
        2.  **Intención:** Clasifica mentalmente el mensaje:
            - ¿Pregunta Coherente? (Relacionada con el negocio).
            - ¿Pregunta Incoherente? (No relacionada).
            - ¿Objeción de Venta? (Expresa una duda o razón para no comprar: "es caro", "no estoy seguro", "necesito pensarlo").
            - ¿Sentimiento Negativo? (Detectar frustración, enojo, grosería).

        **FASE 2: SELECCIÓN DE ESTRATEGIA DE RESPUESTA**
        - **Si es Coherente:** Responde con la información de la base de conocimiento, pero siempre conecta la respuesta con un BENEFICIO claro para el cliente y termina con una pregunta abierta para mantener el control de la conversación.
        - **Si es Incoherente (Ej: 'venden carne'):** Responde cortésmente a su pregunta y PIVOTA INMEDIATAMENTE hacia el negocio. Usa una transición fluida.
        - **Si es una Objeción (Ej: 'es muy caro'):** ¡Activa el modo "Derribo de Dolores"! Usa la táctica 'Validar -> Empatizar -> Refutar'.
        - **Si es Enojo/Grosería:** NUNCA pelees. Desescala con calma. Ignora el insulto, valida la frustración y enfócate 100% en la SOLUCIÓN práctica.

        **FASE 3: CONSTRUCCIÓN PERSUASIVA DE LA RESPUESTA (Tu Arsenal Táctico)**
        Al redactar CADA respuesta, debes aplicar estas técnicas:
        - **Anticipa Dolores:** Piensa en las objeciones comunes y derríbalas proactivamente.
        - **Gatillos de Marketing:** Usa escasez, urgencia y prueba social de forma sutil.
        - **Protocolo de Precios:** Si preguntan por el precio, responde con el precio, INMEDIATAMENTE describe las 2 características más valiosas, anticipa y derriba las 2 objeciones más comunes, y termina con una pregunta abierta.
        
        ### REGLA FINAL Y MÁS IMPORTANTE ###
        Todo el análisis de las Fases 1 y 2 es tu proceso de pensamiento interno. NUNCA debes mostrarle al cliente las palabras "FASE 1", "DIAGNÓSTICO", "ESTRATEGIA" o "CONSTRUCCIÓN". El cliente solo debe ver la respuesta final, natural y fluida que construyes en la Fase 3.
        """
        try:
            self.model = genai.GenerativeModel('models/gemini-pro-latest')
            # La arquitectura correcta: el chat se inicia UNA SOLA VEZ, con la personalidad.
            self.chat = self.model.start_chat(history=[
                {'role': 'user', 'parts': [protocolo_vendedor_consultor]},
                {'role': 'model', 'parts': ["Protocolo 'Vendedor Profesional' cargado. Estoy listo para convertir."]}
            ])
            print(">>> [Cerebro] Modelo de IA y chat con personalidad inicializados correctamente.")
        except Exception as e:
            print(f"!!! ERROR [Cerebro]: No se pudo inicializar el modelo o el chat. {e} !!!")

    def invoke(self, input_data):
        if not self.chat:
            return "Lo siento, el cerebro de la IA no está disponible en este momento debido a un error de inicialización."
        
        question = input_data.get("question")
        if not question:
            return "Error interno: No se recibió ninguna pregunta."
            
        try:
            # Ahora solo enviamos el mensaje, porque el chat ya tiene la personalidad y la memoria.
            response = self.chat.send_message(question)
            return response.text
        except Exception as e:
            print(f"!!! ERROR [Cerebro]: Ocurrió un error al enviar el mensaje a la IA. {e} !!!")
            return "En este momento, parece que hubo una pequeña incidencia al procesar tu solicitud. ¿Podrías intentar reformular tu pregunta?"

def create_chatbot(descripcion_producto: str):
    if not descripcion_producto:
        print("!!! WARNING [create_chatbot]: Se recibió una descripción vacía. Usando personalidad genérica.")
        descripcion_producto = "un asistente de negocios general"

    brain_instance = DashboardBrain(descripcion_producto)
    
    if brain_instance.chat: # Verificamos si el chat (que incluye el modelo) se creó bien.
        print(">>> [create_chatbot] Instancia del cerebro creada y lista para operar.")
        return brain_instance
    else:
        print("!!! ERROR [create_chatbot]: La creación de la instancia del cerebro falló.")
        return None
