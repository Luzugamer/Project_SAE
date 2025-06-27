from django.urls import path
from . import views

urlpatterns = [
    # Vista principal del repositorio
    path('repositorio/', views.vista_repositorio, name='repositorio'),

    # Vista para mostrar exámenes por universidad (opcional)
    path('repositorio/universidad/<int:universidad_id>/', views.vista_examenes_universidad, name='examenes_universidad'),

    # Endpoint AJAX para cargar exámenes dinámicamente
    path('repositorio/universidad/<int:universidad_id>/examenes/', views.examenes_ajax, name='examenes_ajax'),

    # Agregar universidad (repositorio)
    path('repositorio/add-universidad/', views.add_universidad, name='add_universidad'),

    # Agregar examen a universidad específica
    path('repositorio/universidad/<int:universidad_id>/add-examen/', views.add_examen, name='add_examen'),

    # Editar examen desde el formulario emergente
    path('repositorio/examen/<int:examen_id>/editar/', views.editar_examen, name='editar_examen'),

    # Eliminar examen con confirmación
    path('repositorio/examen/<int:examen_id>/eliminar/', views.eliminar_examen, name='eliminar_examen'),

    # Editar universidad (repositorio) reutilizando el template de creación
    path('repositorio/universidad/<int:universidad_id>/editar/', views.editar_universidad, name='editar_universidad'),

    # Eliminar universidad con confirmación
    path('repositorio/universidad/<int:universidad_id>/eliminar/', views.eliminar_universidad, name='eliminar_universidad'),
]

