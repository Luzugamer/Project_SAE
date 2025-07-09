# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.lista_cursos, name='lista_cursos'),
    path('curso/<int:curso_id>/', views.detalle_curso, name='detalle_curso'),
]
