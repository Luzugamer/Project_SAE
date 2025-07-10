from django.urls import path
from . import views

urlpatterns = [
    path('escaner/test/', views.test_escaneo, name='test_escaneo'),
    path('escanear/', views.escanear_archivo, name='escanear_archivo'),
]
