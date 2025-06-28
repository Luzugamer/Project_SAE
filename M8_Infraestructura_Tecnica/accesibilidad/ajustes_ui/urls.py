from django.urls import path
from .views import ajustes_ui_inicio

urlpatterns = [
    path('', ajustes_ui_inicio, name='ajustes_ui_index'),
]
