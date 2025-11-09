import os
import json
import psycopg2
from dotenv import load_dotenv
import google.generativeai as genai

# --- CONFIGURACIÓN ---
load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Configurar la IA de Google
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print(">>> IA de Google configurada exitosamente.")
else:
    print("!!! ADVERTENCIA: GOOGLE_API_KEY no encontrada. El Persuasor no puede funcionar.")

# --- FUNCIÓN DE PERSUASIÓN CON IA ---
def generar_borrador_con_ia(nombre_negocio, informe_analisis, servicio_ofrecido):
    if not GOOGLE_API_KEY:
        return "Error: GOOGLE_API_KEY no configurada."

    # Extraemos los puntos de dolor del informe para usarlos en el prompt
    puntos_de_dolor = informe_analisis.get("puntos_de_dolor", [])
    inteligencia_adicional = informe_analisis.get("inteligencia_adicional", {})
    queja_principal = inteligencia_adicional.get("queja_principal_resenas", "No especificada")

    # Convertimos la lista de puntos de dolor en un texto legible
    texto_puntos_de_dolor = ", ".join(puntos_de_dolor).replace("_", " ") if puntos_de_dolor else "No se encontraron puntos de dolor específicos, pero siempre hay áreas de mejora en la comunicación digital."

    prompt = f"""
    Actúa como un consultor de marketing digital experto y amigable llamado Moises Bove, CEO de AutoNeura AI.
    Tu misión es redactar un borrador de correo electrónico corto, profesional y muy personalizado (menos de 150 palabras) para el negocio llamado "{nombre_negocio}".

    Esta es la inteligencia que hemos recopilado sobre ellos:
    - Puntos de dolor identificados: {texto_puntos_de_dolor}.
    - Queja principal en sus reseñas (si aplica): {queja_principal}.
    
    El servicio que ofreces para solucionar estos problemas es: {servicio_ofrecido}.

    INSTRUCCIONES PARA EL EMAIL:
    1.  **Apertura Personalizada:** Empieza con un saludo cordial y directo al negocio.
    2.  **Demostración de Valor:** Menciona sutilmente uno de los puntos de dolor que encontraste, demostrando que has hecho tu investigación. No los acuses, preséntalo como una oportunidad de mejora.
    3.  **Presentación de la Solución:** Conecta tu servicio como la solución lógica a ese problema específico.
    4.  **Llamada a la Acción (CTA) de Baja Fricción:** Termina con una pregunta abierta y fácil de responder, como "¿Estarían abiertos a una demostración rápida de 15 minutos la próxima semana para ver cómo esto podría beneficiarlos?".
    5.  **Cierre:** Un cierre profesional: "Saludos cordiales, Moises Bove, CEO de AutoNeura AI".

    No incluyas el asunto del email, solo el cuerpo del mensaje.
    """
    
    try:
        print(f"--- Enviando prompt a la IA para '{nombre_negocio}'...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        borrador = response.text.strip()
        print(">>> Borrador de IA recibido exitosamente.")
        return borrador
    except Exception as e:
        print(f"!!! ERROR durante la generación de IA: {e}")
        return f"Error al generar el borrador: {e}"

# --- FUNCIÓN PRINCIPAL DEL PERSUASOR ---
def persuadir_prospecto():
    print("\n--- Trabajador Persuasor v1.0 INICIADO ---")
    
    conn = None
    prospecto_id = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Buscamos un prospecto analizado y listo para ser persuadido
        cur.execute("SELECT id, nombre_negocio, informe_analisis FROM prospectos WHERE estado = 'analizado_exitoso' LIMIT 1")
        prospecto = cur.fetchone()
        
        if not prospecto:
            print(">>> No se encontraron nuevos prospectos para persuadir. Misión cumplida.")
            return

        prospecto_id, nombre, informe_json = prospecto
        print(f">>> Prospecto encontrado para persuadir: {nombre} (ID: {prospecto_id})")
        
        cur.execute("UPDATE prospectos SET estado = 'en_persuasion' WHERE id = %s", (prospecto_id,))
        conn.commit()

        # Definimos el servicio que estamos vendiendo (esto vendrá de la campaña en el futuro)
        servicio_a_vender = "un Agente de IA personalizado que responde a clientes 24/7, captura leads y aumenta las ventas."
        
        # Llamamos a la IA para generar el mensaje
        borrador_mensaje = generar_borrador_con_ia(nombre, informe_json, servicio_a_vender)
        
        print("--- ¡PERSUASIÓN COMPLETADA! Guardando borrador... ---")
        
        # Guardamos el borrador y actualizamos el estado final
        cur.execute(
            "UPDATE prospectos SET estado = %s, borrador_mensaje = %s WHERE id = %s",
            ('listo_para_revision', borrador_mensaje, prospecto_id)
        )
        conn.commit()
        print(">>> Borrador guardado en la base de datos.")

    except Exception as e:
        print(f"!!! Ocurrió un error catastrófico en el Persuasor: {e} !!!")
        if conn and prospecto_id:
            cur.execute("UPDATE prospectos SET estado = 'analizado_con_error_persuasion' WHERE id = %s", (prospecto_id,))
            conn.commit()
    finally:
        if conn:
            cur.close()
            conn.close()

# --- EJECUCIÓN DEL SCRIPT ---
if __name__ == "__main__":
    persuadir_prospecto()
