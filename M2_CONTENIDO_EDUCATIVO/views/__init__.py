from .repositorio_views import vista_repositorio, vista_examenes_universidad, examenes_ajax
from .universidad_views import add_universidad_admision, add_solucionario_general, editar_universidad, eliminar_universidad
from .examen_views import add_examen, editar_examen, eliminar_examen
from .base import tiene_permiso_profesor_sobre

__all__ = [
    'vista_repositorio',
    'vista_examenes_universidad',
    'examenes_ajax',
    'add_universidad_admision',
    'add_solucionario_general',
    'editar_universidad',
    'eliminar_universidad',
    'add_examen',
    'editar_examen',
    'eliminar_examen',
    'tiene_permiso_profesor_sobre'
]
