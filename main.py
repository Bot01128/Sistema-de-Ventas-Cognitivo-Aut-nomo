import os
import psycopg2
import json
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from flask_babel import Babel
# ¡Importamos las funciones del cerebro!
from cerebro_dashboard import obtener_cerebro, obtener_prompt_sistema

# --- CONFIGURACIÓN INICIAL ---
app = Flask(__name__)
# ... (Tu configuración de Babel y otras variables) ...

# Configurar la IA de Google globalmente (¡CRÍTICO!)
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print(">>> IA de Google configurada exitosamente.")
else:
    print("!!! ADVERTENCIA: GOOGLE_API_KEY no encontrada.")

# Obtenemos el cerebro una sola vez al arrancar
dashboard_brain = obtener_cerebro()
prompt_sistema_cerebro = obtener_prompt_sistema()

# --- RUTA DE CHAT (¡CORREGIDA!) ---
@app.route('/chat', methods=['POST'])
def chat():
    if not dashboard_brain:
        return jsonify({"error": "Cerebro no disponible."}), 500
    
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No hay mensaje."}), 400
        
    try:
        full_prompt = f"{prompt_sistema_cerebro}\n\nUsuario: {user_message}\nAsistente:"
        response = dashboard_brain.generate_content(full_prompt)
        ai_response = response.text.strip()
        return jsonify({"response": ai_response})
    except Exception as e:
        print(f"!!! ERROR al procesar chat: {e} !!!")
        return jsonify({"error": "Ocurrió un error al procesar."}), 500

# ... (El resto de tus rutas, como '/', '/crear-campana', etc., van aquí sin cambios) ...

# --- BLOQUE DE ARRANQUE ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)```

---

### **Frente #2: Validación Inteligente (No solo si está vacío)**

**Diagnóstico:** Tienes razón. Nuestro "espía" actual es tonto. Solo comprueba si un campo está vacío, pero no si lo que escribiste tiene sentido.

**Solución (El "Espía" con Ojos):**
Vamos a mejorar la lógica de validación en `dashboard.html`. Usaremos "expresiones regulares" (pequeños patrones de texto) para verificar que la información parezca real.

1.  En tu `dashboard.html`, en la sección `<script>`, busca el bloque del `lanzarBtn.addEventListener`.
2.  **Reemplaza** la `const fieldsToValidate` con esta versión más inteligente:

```javascript
const fieldsToValidate = [
    { id: 'nombre_campana', tab: 'campaign', message: 'Por favor, dale un nombre a tu campaña.', minLength: 5 },
    { id: 'que_vendes', tab: 'campaign', message: 'Por favor, describe qué vendes.', minLength: 10 },
    { id: 'a_quien_va_dirigido', tab: 'campaign', message: 'Por favor, especifica a quién va dirigido.', minLength: 10 },
    { id: 'descripcion_producto', tab: 'data', message: 'La descripción del producto es necesaria.', minLength: 20 },
    { id: 'numero_whatsapp', tab: 'data', message: 'Introduce un número de WhatsApp válido.', pattern: /^\+?[1-9]\d{1,14}$/ },
    { id: 'enlace_venta', tab: 'data', message: 'Introduce una URL válida (ej: https://...).', pattern: /^(https|http):\/\/[^ "]+$/ }
];
