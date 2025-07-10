from django.db import models

class ArchivoEscaneado(models.Model):
    nombre_archivo = models.CharField(max_length=255)
    archivo_pdf = models.FileField(upload_to='examenes/')
    texto_extraido = models.TextField(blank=True, null=True)
    fecha_escaneo = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_archivo