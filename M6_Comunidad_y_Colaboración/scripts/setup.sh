#!/bin/bash

echo "Configurando Asistente IA..."

# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear base de datos
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic --noinput

# Crear directorios necesarios
mkdir -p logs
mkdir -p media

echo "Configuración completada!"
echo "Para iniciar el servidor: python manage.py runserver"