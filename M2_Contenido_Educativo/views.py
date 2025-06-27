from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import Universidad, Examen
from .forms import UniversidadForm, ExamenForm


def vista_repositorio(request):
    universidades = Universidad.objects.all()
    return render(request, 'repositorio/repositorio.html', {'universidades': universidades})


def add_universidad(request):
    if request.method == 'POST':
        form = UniversidadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('repositorio')
    else:
        form = UniversidadForm()
    return render(request, 'repositorio/add_universidad.html', {'form': form})


def vista_examenes_universidad(request, universidad_id):
    universidad = get_object_or_404(Universidad, id=universidad_id)
    examenes = universidad.examenes.all()
    return render(request, 'repositorio/examenes_por_universidad.html', {
        'universidad': universidad,
        'examenes': examenes
    })


def examenes_ajax(request, universidad_id):
    universidad = get_object_or_404(Universidad, id=universidad_id)
    examenes = universidad.examenes.all()

    examenes_data = [{
        'id': examen.id,
        'nombre': examen.nombre,
        'fecha': str(examen.fecha),
        'archivo': examen.archivo.url if examen.archivo else ''
    } for examen in examenes]

    return JsonResponse({'examenes': examenes_data})


def add_examen(request, universidad_id):
    universidad = get_object_or_404(Universidad, id=universidad_id)
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        fecha = request.POST.get('fecha')
        archivo = request.FILES.get('archivo')

        if nombre and archivo and fecha:
            Examen.objects.create(
                universidad=universidad,
                nombre=nombre,
                fecha=fecha,
                archivo=archivo
            )
    return redirect('repositorio')


def editar_universidad(request, universidad_id):
    universidad = get_object_or_404(Universidad, id=universidad_id)
    form = UniversidadForm(request.POST or None, request.FILES or None, instance=universidad)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Repositorio actualizado correctamente.')
        return redirect('repositorio')

    # Si es una petición AJAX, devolver solo el formulario como fragmento
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'repositorio/form_fragmento.html', {'form': form})

    # En caso contrario, usar la vista completa
    return render(request, 'repositorio/add_universidad.html', {'form': form})


def eliminar_universidad(request, universidad_id):
    universidad = get_object_or_404(Universidad, id=universidad_id)
    universidad.delete()
    return JsonResponse({'mensaje': 'Repositorio eliminado correctamente.'})


def editar_examen(request, examen_id):
    examen = get_object_or_404(Examen, id=examen_id)
    form = ExamenForm(request.POST or None, request.FILES or None, instance=examen)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Examen actualizado correctamente.')
        return redirect('repositorio')

    # Si es una petición AJAX, devolver solo el fragmento del formulario
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'repositorio/form_fragmento.html', {'form': form})

    # Si se intenta acceder directamente, prevenir error
    return JsonResponse({'error': 'Acceso no permitido sin AJAX'}, status=400)


def eliminar_examen(request, examen_id):
    examen = get_object_or_404(Examen, id=examen_id)
    examen.delete()
    return JsonResponse({'mensaje': 'Examen eliminado correctamente.'})
