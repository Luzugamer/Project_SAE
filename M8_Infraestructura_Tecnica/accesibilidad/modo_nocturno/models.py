from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ModoNocturno(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    modo_activado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.usuario.username} - {'Activo' if self.modo_activado else 'Desactivado'}"
