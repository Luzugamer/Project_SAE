from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from M1_Gestion_de_Usuarios.decorators import rol_requerido
from M5_cursos_contenido.models import Curso


def pag_descripcion(request):
    return render(request, 'Paginas_Inicio/pag_descripcion.html')

@login_required
def pag_principal(request):
    return render(request, 'Paginas_Inicio/pag_principal.html')

@login_required
@rol_requerido('estudiante')
def pag_estu(request):
    return render(request, 'Paginas_Inicio/pag_principal.html')

@login_required
@rol_requerido('profesor')
def pag_profe(request):
    return render(request, 'Paginas_Inicio/pag_principal.html')

def pagina_principal(request):
    cursos = Curso.objects.all()
    return render(request, 'Paginas_Inicio/pag_principal.html', {'cursos': cursos})
