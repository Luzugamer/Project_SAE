from django.urls import path
from . import views

app_name = 'accesibilidad'

urlpatterns = [
    path('', views.accesibilidad_index, name='index'),
]