
from django.urls import path
from . import views

urlpatterns = [
    path('generador/test/', views.test_generador, name='test_generador'),
]
