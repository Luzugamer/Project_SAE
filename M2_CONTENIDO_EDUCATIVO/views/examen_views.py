from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone

from .base import tiene_permiso_profesor_sobre
from M2_CONTENIDO_EDUCATIVO.models import Examen
from M2_CONTENIDO_EDUCATIVO.forms import ExamenForm
from M2_CONTENIDO_EDUCATIVO.models import Universidad

def add_examen(request, universidad_id):
    universidad = get_object_or_404(Universidad, id=universidad_id)

    if not tiene_permiso_profesor_sobre(request.user, universidad):
        mensaje = {'error': 'Acceso no autorizado'}
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(mensaje, status=403)
        return redirect('repositorio')

    if request.method == 'POST':
        form = ExamenForm(request.POST, request.FILES)
        if form.is_valid():
            examen = form.save(commit=False)
            examen.universidad = universidad
            examen.codigo_modular = universidad.codigo_modular

            try:
                examen.save()
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Examen agregado exitosamente',
                        'examen_id': examen.id,
                    })
                messages.success(request, 'Examen agregado correctamente')
                return redirect('vista_examenes_universidad', universidad_id=universidad.id)
            except Exception as e:
                mensaje_error = str(e)
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': mensaje_error}, status=500)
                messages.error(request, f"Error al guardar: {mensaje_error}")
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = ExamenForm(initial={'fecha': timezone.now().strftime('%Y-%m-%d')})

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'repositorio/form_fragmento.html', {
            'form': form,
            'form_action': reverse('add_examen', args=[universidad.id])
        })

    return render(request, 'repositorio/examenes_por_universidad.html', {
        'universidad': universidad,
        'form': form,
        'mostrar_formulario': True
    })

def editar_examen(request, examen_id):
    examen = get_object_or_404(Examen, id=examen_id)
    universidad = examen.universidad
    
    if not tiene_permiso_profesor_sobre(request.user, universidad):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'No tienes permisos para editar este examen'}, status=403)
        messages.error(request, 'No tienes permisos para editar este examen.')
        return redirect('repositorio')

    form = ExamenForm(request.POST or None, request.FILES or None, instance=examen)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Examen actualizado correctamente'})
            messages.success(request, 'Examen actualizado correctamente.')
            return redirect('repositorio')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'repositorio/form_fragmento.html', {
            'form': form,
            'form_action': reverse('editar_examen', args=[examen.id])
        })

    return render(request, 'repositorio/editar_examen.html', {
        'form': form,
        'examen': examen
    })

def eliminar_examen(request, examen_id):
    examen = get_object_or_404(Examen, id=examen_id)
    universidad = examen.universidad

    if not tiene_permiso_profesor_sobre(request.user, universidad):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'No tienes permisos para eliminar este examen'}, status=403)
        messages.error(request, 'No tienes permisos para eliminar este examen.')
        return redirect('repositorio')

    try:
        examen.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Examen eliminado correctamente'})
        messages.success(request, 'Examen eliminado correctamente.')
        return redirect('repositorio')
    except Exception as e:
        error_msg = f"Error al eliminar el examen: {str(e)}"
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg}, status=500)
        messages.error(request, error_msg)
        return redirect('repositorio')