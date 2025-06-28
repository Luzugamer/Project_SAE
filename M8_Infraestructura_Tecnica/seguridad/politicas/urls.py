from django.urls import path
from . import views
from .views import PoliticasPrivacidadView  # Asegúrate de que esta vista exista

urlpatterns = [
    path('', PoliticasPrivacidadView.as_view(), name='politicas_index'),  # Vista basada en clase
    path('config/', views.configuracion, name='politicas_config'),  # Vista basada en función
]