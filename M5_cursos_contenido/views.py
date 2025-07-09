from django.shortcuts import render, get_object_or_404
from M5_cursos_contenido.models import Curso, Tema, Examen, Leccion


def lista_cursos(request):
    cursos = Curso.objects.all()
    return render(request, 'contenido_cursos/lista_cursos.html', {'cursos': cursos})

def detalle_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    temas = Tema.objects.filter(curso=curso)
    examenes = Examen.objects.filter(curso = curso)
    lecciones = Leccion.objects.filter(curso = curso)
    return render(request, 'contenido_cursos/detalle_curso.html', {
        'curso': curso, 
        'temas': temas, 
        'examenes': examenes,
        'lecciones': lecciones
    })
