import re

def limpiar_texto(texto):
    texto = re.sub(r'\s+', ' ', texto)  # Eliminar espacios duplicados
    texto = texto.strip()
    return texto