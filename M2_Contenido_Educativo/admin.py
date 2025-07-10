from django.contrib import admin
from .models import Universidad, Examen
from django.utils.html import format_html

@admin.register(Universidad)
class UniversidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'pais', 'tipo_solucionario', 'ver_logo')
    search_fields = ('nombre',)
    list_filter = ('pais', 'tipo_solucionario')

    def ver_logo(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;" />', obj.logo.url)
        return "Sin logo"
    ver_logo.short_description = "Logo"

@admin.register(Examen)
class ExamenAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha', 'universidad', 'ver_miniatura')
    search_fields = ('nombre', 'fecha')
    list_filter = ('universidad',)

    def ver_miniatura(self, obj):
        if obj.miniatura:
            return format_html('<img src="{}" width="80" height="100" style="object-fit:contain;" />', obj.miniatura.url)
        return "Sin miniatura"
    ver_miniatura.short_description = "Miniatura"
