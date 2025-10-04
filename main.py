from flask import Flask, render_template
import os

app = Flask(__name__)

# Esta será la ruta principal que mostrará nuestro Dashboard
@app.route('/')
def dashboard():
    # Le decimos a Flask que busque y muestre el archivo 'dashboard.html'
    # que estará en una carpeta llamada 'templates'
    return render_template('dashboard.html')

if __name__ == '__main__':
    # Esto permite que el servidor se ejecute localmente para pruebas
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
