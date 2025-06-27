from django.db import models

TIPO_SOLUCIONARIO_CHOICES = [
    ('admision', 'Solucionario de Examen de Admisión'),
    ('ejercicios', 'Solucionario de Ejercicios'),
    ('otro', 'Otro'),
]

class Universidad(models.Model):
    nombre = models.CharField(max_length=255)
    pais = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logos_universidades/')
    especialidad = models.CharField(max_length=255, blank=True, null=True)
    tipo_solucionario = models.CharField(max_length=20, choices=TIPO_SOLUCIONARIO_CHOICES, default='admision')


class Examen(models.Model):
    universidad = models.ForeignKey(Universidad, on_delete=models.CASCADE, related_name='examenes')
    nombre = models.CharField(max_length=255)
    fecha = models.CharField(max_length=50)
    archivo = models.FileField(upload_to='examenes/', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.fecha}"
