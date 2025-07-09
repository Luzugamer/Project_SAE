from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
import uuid
import logging

# Configuración del logger
logger = logging.getLogger(__name__)

ROLES = (
    ('profesor', 'Profesor'),
    ('estudiante', 'Estudiante')
)

ESTADO_MIEMBRO = (
    ('activo', 'Activo'),
    ('inactivo', 'Inactivo'),
)

TIPO_MENSAJE = (
    ('publico', 'Público'),
    ('privado', 'Privado'),
    ('sistema', 'Sistema'),
)
class Conversacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'conversaciones'
        ordering = ['-fecha_creacion']
        
class Comunidad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    icono = models.ImageField(upload_to='iconos/', null=True, blank=True)
    institucion_afiliada = models.CharField(max_length=200, blank=True, null=True)
    creador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comunidades_creadas')
    miembros = models.ManyToManyField(settings.AUTH_USER_MODEL, through='MiembroComunidad', related_name='comunidades')
    puntos_prestigio = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    es_destacada = models.BooleanField(default=False)
    codigo_invitacion = models.CharField(max_length=10, unique=True, blank=True)
    activa = models.BooleanField(default=True)
    chat_activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering = ['-fecha_creacion']
    
    # Nuevos campos para notificaciones por email
    notificaciones_email = models.BooleanField(default=True, help_text="Enviar notificaciones por email")
    email_notificacion = models.EmailField(
        blank=True, 
        null=True, 
        help_text="Email personalizado para notificaciones (opcional)"
    )

    def save(self, *args, **kwargs):
        if not self.codigo_invitacion:
            self.codigo_invitacion = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def get_miembros_activos(self):
        return self.miembrocomunidad_set.filter(estado='activo')

    def get_miembros_inactivos(self):
        return self.miembrocomunidad_set.filter(estado='inactivo')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Comunidades"

class MiembroComunidad(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)
    fecha_union = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADO_MIEMBRO, default='activo')
    rol = models.CharField(max_length=10, choices=ROLES, default='estudiante')
    ultima_conexion = models.DateTimeField(auto_now=True)
    en_linea = models.BooleanField(default=False)

    class Meta:
        unique_together = ['usuario', 'comunidad']

    def __str__(self):
        return f"{self.usuario.username} en {self.comunidad.nombre}"
    
    @property
    def nombre_completo(self):
        return self.usuario.get_full_name()

class Mensaje(models.Model):
    TIPO_MENSAJE = (
        ('publico', 'Publico'),
        ('privado', 'Privado'),
        ('sistema', 'Sistema'),
        ('usuario', 'Usuario'),
        ('ia', 'IA'),
    )

    comunidad = models.ForeignKey(
        Comunidad,
        on_delete=models.CASCADE,
        related_name='mensajes',
        null=True,
        blank=True,
    )
    conversacion = models.ForeignKey(
        Conversacion,
        on_delete=models.CASCADE,
        related_name='mensajes',
        null=True,
        blank=True,
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Usuario que envio el mensaje (si aplica)"
    )
    contenido = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    tipo = models.CharField(max_length=10, choices=TIPO_MENSAJE)
    es_importante = models.BooleanField(default=False)
    editado = models.BooleanField(default=False)
    fecha_edicion = models.DateTimeField(null=True, blank=True)

    # Solo para mensajes IA
    tokens_utilizados = models.IntegerField(default=0, blank=True, null=True)
    tiempo_respuesta = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'mensajes'
        ordering = ['-timestamp']

    def es_vigente(self):
        return True  # Podrías añadir lógica con `fecha_expiracion` si deseas

    def __str__(self):
        if self.comunidad:
            return f"[Comunidad] {self.autor.username if self.autor else 'IA'} en {self.comunidad.nombre}: {self.contenido[:50]}"
        elif self.conversacion:
            return f"[IA] {self.tipo.upper()} - {self.contenido[:50]}"
        return f"[Mensaje] {self.contenido[:50]}"



class MensajePrivado(models.Model):
    """Modelo para mensajes privados entre miembros de la comunidad"""
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE, related_name='mensajes_privados')
    remitente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mensajes_enviados')
    destinatario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mensajes_recibidos')
    contenido = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)
    fecha_lectura = models.DateTimeField(null=True, blank=True)

    def marcar_como_leido(self):
        if not self.leido:
            self.leido = True
            self.fecha_lectura = timezone.now()
            self.save()

    def __str__(self):
        return f"De {self.remitente.username} para {self.destinatario.username}"

    class Meta:
        ordering = ['-timestamp']

class SalaChat(models.Model):
    """Salas de chat específicas dentro de una comunidad"""
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE, related_name='salas_chat')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    creada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    activa = models.BooleanField(default=True)
    solo_profesores = models.BooleanField(default=False)
    participantes = models.ManyToManyField(settings.AUTH_USER_MODEL, through='ParticipanteSala', related_name='salas_participando')
   
    def es_vigente(self):
        """Considera que un mensaje es vigente si fue creado hace menos de 7 días"""
        return timezone.now() <= self.fecha_creacion + timedelta(days=7)
   
    def __str__(self):
        return f"{self.nombre} - {self.comunidad.nombre}"

    class Meta:
        unique_together = ['comunidad', 'nombre']

class ParticipanteSala(models.Model):
    """Participantes en una sala de chat específica"""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sala = models.ForeignKey(SalaChat, on_delete=models.CASCADE)
    fecha_union = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    ultimo_mensaje_visto = models.ForeignKey('MensajeSala', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ['usuario', 'sala']

class MensajeSala(models.Model):
    """Mensajes dentro de salas de chat específicas"""
    sala = models.ForeignKey(SalaChat, on_delete=models.CASCADE, related_name='mensajes')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contenido = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    editado = models.BooleanField(default=False)
    fecha_edicion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.autor.username} en {self.sala.nombre}: {self.contenido[:30]}"

    class Meta:
        ordering = ['timestamp']

class ConexionUsuario(models.Model):
    """Rastrea las conexiones de usuarios para estado en línea"""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, unique=True)
    timestamp_conexion = models.DateTimeField(auto_now_add=True)
    timestamp_desconexion = models.DateTimeField(null=True, blank=True)
    activa = models.BooleanField(default=True)

    def desconectar(self):
        self.activa = False
        self.timestamp_desconexion = timezone.now()
        self.save()

    class Meta:
        unique_together = ['usuario', 'comunidad', 'session_key']

class HistorialMensajes(models.Model):
    """Almacena temporalmente los mensajes para recuperación posterior"""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)
    contenido = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    tipo_mensaje = models.CharField(max_length=10, choices=TIPO_MENSAJE, default='publico')
    destinatario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                   related_name='mensajes_recibidos_historial', null=True, blank=True)
    
    # Campos para limpieza automática
    fecha_expiracion = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        if not self.fecha_expiracion:
            # Los mensajes se guardan por 30 días por defecto
            self.fecha_expiracion = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Historial: {self.usuario.username} - {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']

class Perfil(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    estado_chat = models.CharField(max_length=20, 
                                 choices=[
                                     ('disponible', 'Disponible'),
                                     ('ocupado', 'Ocupado'),
                                     ('ausente', 'Ausente'),
                                     ('no_molestar', 'No molestar')
                                 ], 
                                 default='disponible')

    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_display()}"
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

class Invitacion(models.Model):
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)
    invitado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invitaciones_enviadas')
    invitado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invitaciones_recibidas')
    fecha_invitacion = models.DateTimeField(auto_now_add=True)
    aceptada = models.BooleanField(default=False)
    procesada = models.BooleanField(default=False)

    class Meta:
        unique_together = ['comunidad', 'invitado']

class Reporte(models.Model):
    MOTIVOS = (
        ('spam', 'Spam'),
        ('contenido_inapropiado', 'Contenido inapropiado'),
        ('acoso', 'Acoso'),
        ('otro', 'Otro'),
    )
    
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)
    reportado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    motivo = models.CharField(max_length=80, choices=MOTIVOS)
    descripcion = models.TextField()
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    procesado = models.BooleanField(default=False)

    def __str__(self):
        return f"Reporte de {self.reportado_por.username} sobre {self.comunidad.nombre}"

class ProblemaMatematico(models.Model):
    NIVELES = [
        ('secundaria', '5to Secundaria'),
        ('universitario', 'Universitario'),
    ]
    
    CATEGORIAS = [
        ('algebra', 'Algebra'),
        ('calculo', 'Calculo'),
        ('geometria', 'Geometria'),
        ('estadistica', 'Estadistica'),
        ('trigonometria', 'Trigonometria'),
        ('ecuaciones', 'Ecuaciones'),
        ('otro', 'Otro'),
    ]
    
    mensaje = models.OneToOneField(Mensaje, on_delete=models.CASCADE)
    nivel = models.CharField(max_length=20, choices=NIVELES)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    dificultad = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    resuelto = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'problemas_matematicos'