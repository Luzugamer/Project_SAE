from django.urls import path
from .views import (
    vista_repositorio,
    examenes_ajax,
    add_universidad_admision,
    add_solucionario_general,
    editar_universidad,
    eliminar_universidad,
    add_examen,
    editar_examen,
    eliminar_examen,
)

urlpatterns = [
    path('repositorio/', vista_repositorio, name='repositorio'),
    path('repositorio/universidad/<int:universidad_id>/examenes/', examenes_ajax, name='examenes_ajax'),

    path('repositorio/add-universidad/admision/', add_universidad_admision, name='add_universidad_admision'),
    path('repositorio/add-universidad/general/', add_solucionario_general, name='add_solucionario_general'),
    path('repositorio/universidad/<int:universidad_id>/editar/', editar_universidad, name='editar_universidad'),
    path('repositorio/universidad/<int:universidad_id>/eliminar/', eliminar_universidad, name='eliminar_universidad'),

    path('repositorio/universidad/<int:universidad_id>/add-examen/', add_examen, name='add_examen'),
    path('repositorio/examen/<int:examen_id>/editar/', editar_examen, name='editar_examen'),
    path('repositorio/examen/<int:examen_id>/eliminar/', eliminar_examen, name='eliminar_examen'),
]
