from django.contrib import admin
from .models import ModoNocturno

@admin.register(ModoNocturno)
class ModoNocturnoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'modo_activado')
