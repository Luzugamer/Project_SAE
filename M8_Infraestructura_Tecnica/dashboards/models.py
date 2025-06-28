from django.db import models

class Dashboard(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Dashboard")
    descripcion = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Dashboard'
        verbose_name_plural = 'Dashboards'