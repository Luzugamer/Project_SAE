from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()  # ✅ Usamos el modelo de usuario correcto

class ConfiguracionAccesibilidad(models.Model):
    """
    Modelo para almacenar configuraciones de accesibilidad
    """
    TEMA_OPCIONES = [
        ('claro', 'Tema Claro'),
        ('oscuro', 'Tema Oscuro'),
        ('alto_contraste', 'Alto Contraste'),
    ]

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='configuracion_accesibilidad'
    )
    tema_preferido = models.CharField(
        max_length=20,
        choices=TEMA_OPCIONES,
        default='claro',
        verbose_name='Tema de color'
    )
    tamano_fuente = models.PositiveIntegerField(
        default=16,
        validators=[MinValueValidator(12), MaxValueValidator(24)],
        verbose_name='Tamaño de fuente (px)'
    )
    activar_lector_pantalla = models.BooleanField(
        default=False,
        verbose_name='Compatibilidad con lector de pantalla'
    )
    subtitulos_automaticos = models.BooleanField(
        default=False,
        verbose_name='Mostrar subtítulos automáticos'
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )

    class Meta:
        verbose_name = 'Configuración de Accesibilidad'
        verbose_name_plural = 'Configuraciones de Accesibilidad'
        ordering =  ['usuario']


    def __str__(self):
        return f"Configuración de {self.usuario.username}"


class RegistroAccesibilidad(models.Model):
    """
    Modelo para registrar eventos de accesibilidad
    """
    TIPO_EVENTO = [
        ('tema', 'Cambio de tema'),
        ('fuente', 'Ajuste de fuente'),
        ('lector', 'Uso de lector pantalla'),
        ('subtitulos', 'Activación subtítulos'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='registros_accesibilidad'
    )
    tipo_evento = models.CharField(
        max_length=20,
        choices=TIPO_EVENTO,
        verbose_name='Tipo de evento'
    )
    valor_anterior = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    valor_nuevo = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro'
    )
    dispositivo = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Registro de Accesibilidad'
        verbose_name_plural = 'Registros de Accesibilidad'
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.usuario.username} - {self.get_tipo_evento_display()}"


class PerfilAccesibilidad(models.Model):
    """
    Perfil extendido para preferencias de accesibilidad
    """
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )
    preferencia_animaciones = models.BooleanField(
        default=True,
        verbose_name='Mostrar animaciones'
    )
    nivel_contraste = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Nivel de contraste (1-5)'
    )
    atajos_teclado = models.JSONField(
        default=dict,
        verbose_name='Atajos de teclado personalizados'
    )

    def __str__(self):
        return f"Perfil de accesibilidad - {self.usuario.username}"
