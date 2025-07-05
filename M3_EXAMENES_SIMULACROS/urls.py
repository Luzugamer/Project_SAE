
from django.urls import path
from . import views

urlpatterns = [
    path('simulacro/test/', views.test_simulacro, name='test_simulacro'), #temporal, quitar luego
    path('menu_simulacros/', views.menu_simulacros, name='menu_simulacros'),
    path('simulacro_individual/', views.menu_simulacros, name='simulacro_individual'),
    path('simulacro_grupal/', views.menu_simulacros, name='simulacro_grupal'),
    path('resultados/', views.menu_simulacros, name='resultados'),
]
