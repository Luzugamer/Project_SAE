from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UsuarioManager(BaseUserManager):
    def create_user(self, correo_electronico, nombre, apellido, password=None, **extra_fields):
        if not correo_electronico:
            raise ValueError("El correo electrónico es obligatorio")
        correo_electronico = self.normalize_email(correo_electronico)
        user = self.model(correo_electronico=correo_electronico, nombre=nombre, apellido=apellido, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        # Asignar rol por defecto "estudiante" solo si no es staff/superuser
        if not user.is_staff and not user.is_superuser:
            rol_estudiante, created = Rol.objects.get_or_create(
                nombre_rol='estudiante',
                defaults={'descripcion': 'Rol por defecto para estudiantes'}
            )
            UsuarioRol.objects.create(usuario=user, rol=rol_estudiante)
        
        return user

    def create_superuser(self, correo_electronico, nombre, apellido, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        user = self.create_user(correo_electronico, nombre, apellido, password, **extra_fields)
        
        # Asignar rol de admin al superusuario
        rol_admin, created = Rol.objects.get_or_create(
            nombre_rol='admin',
            defaults={'descripcion': 'Administrador del sistema'}
        )
        UsuarioRol.objects.create(usuario=user, rol=rol_admin)
        
        return user

class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    correo_electronico = models.EmailField(unique=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    ultima_sesion = models.DateTimeField(null=True, blank=True)
    cierre_sesion = models.DateTimeField(null=True, blank=True)
    
    # NUEVOS CAMPOS PARA DOCENTES
    codigo_modular = models.CharField(max_length=10, null=True, blank=True)
    institucion_educativa = models.CharField(max_length=255, null=True, blank=True)
    departamento = models.CharField(max_length=100, null=True, blank=True)
    provincia = models.CharField(max_length=100, null=True, blank=True)
    distrito = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = 'correo_electronico'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Rol(models.Model):
    nombre_rol = models.CharField(max_length=255, unique=True)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre_rol

class UsuarioRol(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('usuario', 'rol')