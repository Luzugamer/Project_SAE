from django.urls import path
from .views import modo_nocturno_inicio

urlpatterns = [
    path('', modo_nocturno_inicio, name='modo_nocturno_index'),
]
