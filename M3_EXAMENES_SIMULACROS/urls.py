
from django.urls import path
from . import views

urlpatterns = [
    path('simulacro/test/', views.test_simulacro, name='test_simulacro'), #temporal, quitar luego
    path('menu_simulacros/', views.menu_simulacros, name='menu_simulacros'),
    path('simulacro_individual/', views.simulacro_individual, name='simulacro_individual'),
    path('simulacro_grupal/', views.simulacro_grupal, name='simulacro_grupal'),
    path('resultados/', views.resultados, name='resultados'),

]
