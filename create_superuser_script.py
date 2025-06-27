import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project_SAE.settings')

django.setup()

from M1_Gestion_de_Usuarios.models import Usuario

correo = "leonardopardo2078@gmail.com"
nombre = "L Pardo"
apellido = "Lopez"
password = "Adminadmin123."

if not Usuario.objects.filter(correo_electronico=correo).exists():
    Usuario.objects.create_superuser(
        correo_electronico=correo,
        nombre=nombre,
        apellido=apellido,
        password=password
    )
    print("✅ Superusuario creado correctamente.")
else:
    print("ℹ️ Ya existe un usuario con ese correo.")
