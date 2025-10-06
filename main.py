from flask import Flask, render_template, request
from flask_babel import Babel
import os

app = Flask(__name__)

# --- Configuración de Babel para Internacionalización (Sintaxis Nueva) ---
def get_locale():
    # Detecta el mejor idioma basado en las preferencias del navegador
    return request.accept_languages.best_match(['en', 'es'])

babel = Babel(app, locale_selector=get_locale)

# --- Rutas de la Aplicación ---
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
