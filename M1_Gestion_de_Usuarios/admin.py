from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario

class UsuarioAdmin(BaseUserAdmin):
    # Campos que se mostrarán en la lista de usuarios
    list_display = ('correo_electronico', 'nombre', 'apellido', 'rol', 'is_active', 'is_staff', 'fecha_registro')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'fecha_registro', 'rol')
    
    # Campos para búsqueda
    search_fields = ('correo_electronico', 'nombre', 'apellido')
    
    # Organización de campos en el formulario de edición
    fieldsets = (
        (None, {'fields': ('correo_electronico', 'password')}),
        ('Información Personal', {'fields': ('nombre', 'apellido', 'rol')}),  # Añadido 'rol' aquí
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'fecha_registro', 'ultima_sesion', 'cierre_sesion')}),
    )
    
    # Campos para el formulario de creación de usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('correo_electronico', 'nombre', 'apellido', 'rol', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ('fecha_registro', 'last_login', 'ultima_sesion', 'cierre_sesion')
    
    # Campo de ordenamiento
    ordering = ('correo_electronico',)


# Registrar los modelos
admin.site.register(Usuario, UsuarioAdmin)


# Personalizar el sitio de administración
admin.site.site_header = "Administración SAE"
admin.site.site_title = "SAE Admin"
admin.site.index_title = "Panel de Administración"