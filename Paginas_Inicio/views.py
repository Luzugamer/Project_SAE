from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from M1_Gestion_de_Usuarios.decorators import rol_requerido

def pag_descripcion(request):
    """Vista pública de descripción del sistema"""
    return render(request, 'Paginas_Inicio/pag_descripcion.html')

@login_required
def pag_principal(request):
    """
    Vista principal que redirige según rol o muestra página genérica
    Puede servir como fallback para roles no especificados
    """
    # Obtener el rol del usuario
    rol = request.user.rol
    
    # Puedes personalizar el contexto según el rol
    contexto = {
        'rol': rol,
        'es_estudiante': rol == 'estudiante',
        'es_profesor': rol == 'profesor',
        'es_admin': rol == 'administrador'
    }
    
    return render(request, 'Paginas_Inicio/pag_principal.html', contexto)

@login_required
@rol_requerido('estudiante')
def pag_estu(request):
    """Vista específica para estudiantes (puede usar la misma plantilla con contexto diferente)"""
    return render(request, 'Paginas_Inicio/pag_principal.html', {
        'es_estudiante': True,
        'vista_especifica': 'estudiante'
    })

@login_required
@rol_requerido('profesor')
def pag_profe(request):
    """Vista específica para profesores"""
    return render(request, 'Paginas_Inicio/pag_principal.html', {
        'es_profesor': True,
        'vista_especifica': 'profesor'
    })