from django.db import models

class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Tema(models.Model):
    curso = models.ForeignKey(Curso, related_name='temas', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    contenido = models.TextField()

    def __str__(self):
        return self.titulo
    
class Examen(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    fecha = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.titulo

class Leccion(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="lecciones")

    def __str__(self):
        return self.titulo

