from django.urls import path
from . import views

urlpatterns = [
    path('escaner/test/', views.test_escaneo, name='test_escaneo'),
]