import os
import psycopg2
import json
import google.generativeai as genai
import uuid
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_babel import Babel
from cerebro_dashboard import create_chatbot

# --- CONFIGURACION INICIAL ---
app = Flask(__name__)
# ¡IMPORTANTE! Necesitamos una "secret_key" para manejar las sesiones de forma segura
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "una-clave-secreta-muy-segura-para-desarrollo")

# --- BLOQUE DE CONFIGURACION DE IDIOMAS ---
# ... (código de Babel sin cambios) ...

# --- INICIALIZACION DE LA APLICACION ---
# ... (código de inicialización de la IA sin cambios) ...

# --- RUTAS DE LA APLICACION ---

# === RUTA RAÍZ INTELIGENTE (VERSIÓN FINAL) ===
@app.route('/')
def home():
    # En el futuro, aquí leeremos el token de la cookie/sesión para verificar
    # Por ahora, si alguien va a la raíz, lo mandamos a login.
    # El JavaScript se encargará de redirigir si ya hay sesión.
    return redirect(url_for('login'))

# === RUTA DE CALLBACK (NUEVA Y CRUCIAL) ===
# Esta es la ruta a la que Supabase nos devuelve después del login.
# Aquí es donde capturamos la sesión.
@app.route('/callback')
def callback():
    # Esta página estará en blanco, su único trabajo es tener un script
    # que capture el token de la URL y lo guarde.
    return render_template('callback.html')

@app.route('/dashboard-ventas')
def sales_dashboard():
    return render_template('dashboard.html')

@app.route('/cliente')
def client_dashboard():
    return render_template('client_dashboard.html')

@app.route('/login')
def login():
    return render_template('login.html')

# ... (resto de las rutas sin cambios) ...

# --- BLOQUE DE ARRANQUE ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
