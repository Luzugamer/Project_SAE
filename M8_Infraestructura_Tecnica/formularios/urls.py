from django.urls import path
from .views import formularios_inicio

urlpatterns = [
    path('', formularios_inicio, name='formularios_inicio'),
]
