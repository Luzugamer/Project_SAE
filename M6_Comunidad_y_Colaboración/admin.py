from django.contrib import admin
from .models import Comunidad, Mensaje, Perfil, MiembroComunidad, Invitacion, Reporte

@admin.register(Comunidad)
class ComunidadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'creador', 'puntos_prestigio', 'es_destacada', 'fecha_creacion', 'activa']
    list_filter = ['es_destacada', 'activa', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion', 'institucion_afiliada']
    readonly_fields = ['codigo_invitacion', 'fecha_creacion']

@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ['autor', 'comunidad', 'timestamp', 'es_importante']
    list_filter = ['timestamp', 'es_importante']
    search_fields = ['contenido', 'autor__username']

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'get_rol_usuario', 'get_institucion_usuario')
    list_filter = ('usuario__rol',)  # Filtro por el campo rol del Usuario
    
    def get_rol_usuario(self, obj):
        return obj.usuario.rol  # Accede al rol a través de la relación
    get_rol_usuario.short_description = 'Rol'
    get_rol_usuario.admin_order_field = 'usuario__rol'  # Permite ordenar
    
    def get_institucion_usuario(self, obj):
        return obj.usuario.institucion  # Accede a la institución a través de la relación
    get_institucion_usuario.short_description = 'Institución'
    get_institucion_usuario.admin_order_field = 'usuario__institucion'

@admin.register(MiembroComunidad)
class MiembroComunidadAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'comunidad', 'rol', 'estado', 'fecha_union']
    list_filter = ['rol', 'estado', 'fecha_union']

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ['reportado_por', 'comunidad', 'motivo', 'fecha_reporte', 'procesado']
    list_filter = ['motivo', 'procesado', 'fecha_reporte']