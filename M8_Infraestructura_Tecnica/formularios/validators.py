# Validadores personalizados 
from django.core.exceptions import ValidationError

def validar_edad(value):
    if value < 5 or value > 100:
        raise ValidationError('Edad debe estar entre 5 y 100 años')

def validar_contraseña_compleja(value):
    if len(value) < 8 or not any(c.isdigit() for c in value):
        raise ValidationError('La contraseña debe tener al menos 8 caracteres y un número')