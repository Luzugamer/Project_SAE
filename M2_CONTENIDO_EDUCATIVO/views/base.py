from M2_CONTENIDO_EDUCATIVO.models import Universidad
from Login.models import UsuarioRol

def tiene_permiso_profesor_sobre(usuario, universidad):
    return (
        UsuarioRol.objects.filter(usuario=usuario, rol__nombre_rol='profesor').exists() and (
            usuario == universidad.profesor_creador or (
                usuario.codigo_modular == universidad.codigo_modular and
                usuario.institucion_educativa == universidad.institucion_educativa
            )
        )
    )