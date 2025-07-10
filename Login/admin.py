from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Rol, UsuarioRol
from .ai_services.ai_client import corregir_institucion_y_ubicacion

class UsuarioRolInline(admin.TabularInline):
    model = UsuarioRol
    extra = 1

class UsuarioAdmin(BaseUserAdmin):
    list_display = (
        'correo_electronico', 'nombre', 'apellido', 'codigo_modular', 
        'institucion_educativa', 'departamento', 'is_active', 'is_staff', 'fecha_registro'
    )
    list_filter = (
        'is_active', 'is_staff', 'is_superuser', 'departamento', 'provincia', 'distrito', 'fecha_registro'
    )

    search_fields = (
        'correo_electronico', 'nombre', 'apellido', 'institucion_educativa', 'codigo_modular'
    )

    fieldsets = (
        (None, {'fields': ('correo_electronico', 'password')}),
        ('Información Personal', {
            'fields': (
                'nombre', 'apellido',
                'codigo_modular', 'institucion_educativa',
                'departamento', 'provincia', 'distrito'
            )
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'fecha_registro', 'ultima_sesion', 'cierre_sesion')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'correo_electronico', 'nombre', 'apellido',
                'password1', 'password2',
                'codigo_modular', 'institucion_educativa',
                'departamento', 'provincia', 'distrito',
                'is_staff', 'is_superuser'
            ),
        }),
    )

    readonly_fields = ('fecha_registro', 'last_login', 'ultima_sesion', 'cierre_sesion')
    ordering = ('correo_electronico',)
    inlines = [UsuarioRolInline]

    def save_model(self, request, obj, form, change):
        print("DEBUG: save_model activado para usuario", obj.correo_electronico)
        if obj.codigo_modular and obj.institucion_educativa:
            datos_corregidos = corregir_institucion_y_ubicacion(
                obj.institucion_educativa,
                obj.departamento,
                obj.provincia,
                obj.distrito
            )
            obj.institucion_educativa = datos_corregidos["nombre_institucion"]
            obj.departamento = datos_corregidos["departamento"]
            obj.provincia = datos_corregidos["provincia"]
            obj.distrito = datos_corregidos["distrito"]

        super().save_model(request, obj, form, change)

class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre_rol', 'descripcion')
    search_fields = ('nombre_rol',)

class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol')
    list_filter = ('rol',)
    search_fields = ('usuario__correo_electronico', 'usuario__nombre', 'rol__nombre_rol')

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Rol, RolAdmin)
admin.site.register(UsuarioRol, UsuarioRolAdmin)

# Personalización del panel
admin.site.site_header = "Administración SAE"
admin.site.site_title = "SAE Admin"
admin.site.index_title = "Panel de Administración"
