from flask import Flask, render_template, request
from flask_babel import Babel, _
import os

app = Flask(__name__)

# --- Configuración de Babel para Internacionalización ---
babel = Babel(app)

@babel.localeselector
def get_locale():
    # Detecta el mejor idioma basado en las preferencias del navegador del usuario
    return request.accept_languages.best_match(['en', 'es'])

# --- Rutas de la Aplicación ---
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
