from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from M1_Gestion_de_Usuarios.decorators import rol_requerido


def pag_descripcion(request):
    return render(request, 'Paginas_Inicio/pag_descripcion.html')

@login_required
@rol_requerido('estudiante')
def pag_estu(request):
    return render(request, 'Paginas_Inicio/pag_principal.html')

@login_required
@rol_requerido('profesor')
def pag_profe(request):
    return render(request, 'Paginas_Inicio/pag_principal.html')
