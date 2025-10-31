# Usa una imagen oficial de Python como base
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requisitos al contenedor
COPY requirements.txt .

# Instala los paquetes de Python necesarios
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de tu aplicación
COPY . .

# Expone el puerto 8080 para que Fly.io pueda conectarse
EXPOSE 8080

# El comando final para ejecutar la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
