from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone

from .base import tiene_permiso_profesor_sobre
from M2_CONTENIDO_EDUCATIVO.models import Examen
from M2_CONTENIDO_EDUCATIVO.forms import ExamenForm
from M2_CONTENIDO_EDUCATIVO.models import Universidad
from M2_CONTENIDO_EDUCATIVO.storage import ExamenesUniversidadesStorage

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone

from .base import tiene_permiso_profesor_sobre
from M2_CONTENIDO_EDUCATIVO.models import Examen
from M2_CONTENIDO_EDUCATIVO.forms import ExamenForm
from M2_CONTENIDO_EDUCATIVO.models import Universidad
from M2_CONTENIDO_EDUCATIVO.storage import ExamenesUniversidadesStorage

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
                        'examen_data': {
                            'id': examen.id,
                            'nombre': examen.nombre,
                            'fecha': examen.fecha.strftime('%Y-%m-%d') if examen.fecha else '',
                            'archivo_url': examen.archivo.url if examen.archivo else '',
                            'miniatura_url': examen.miniatura.url if examen.miniatura else '',
                        }
                    })
                messages.success(request, 'Examen agregado correctamente')
                return redirect('repositorio')
            except Exception as e:
                mensaje_error = str(e)
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': mensaje_error}, status=500)
                messages.error(request, f"Error al guardar: {mensaje_error}")
        else:
            # El formulario no es válido
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            # Para peticiones no-AJAX, mostrar errores y renderizar el formulario
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        # GET request
        form = ExamenForm(initial={'fecha': timezone.now().strftime('%Y-%m-%d')})

    # Respuesta AJAX - retorna solo el fragmento del formulario
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'repositorio/form_fragmento.html', {
            'form': form,
            'form_action': reverse('add_examen', args=[universidad.id]),
            'form_title': 'Agregar Examen',
            'submit_text': 'Agregar Examen'
        })
    
    # Respuesta normal - retorna la página completa del repositorio
    return render(request, 'repositorio/repositorio.html', {
        'form': form,
        'universidad': universidad,
        'form_action': reverse('add_examen', args=[universidad.id])
    })


def editar_examen(request, examen_id):
    examen = get_object_or_404(Examen, id=examen_id)
    universidad = examen.universidad

    if not tiene_permiso_profesor_sobre(request.user, universidad):
        mensaje = 'No tienes permisos para editar este examen.'
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': mensaje}, status=403)
        messages.error(request, mensaje)
        return redirect('repositorio')

    form = ExamenForm(request.POST or None, request.FILES or None, instance=examen)

    if request.method == 'POST':
        if form.is_valid():
            archivo_anterior = examen.archivo
            miniatura_anterior = examen.miniatura
            nuevo_archivo = form.cleaned_data.get('archivo')

            examen_actualizado = form.save(commit=False)

            # Si se sube un nuevo archivo diferente
            if nuevo_archivo and archivo_anterior and archivo_anterior != nuevo_archivo:
                if archivo_anterior.storage.exists(archivo_anterior.name):
                    archivo_anterior.delete(save=False)
                if miniatura_anterior and miniatura_anterior.storage.exists(miniatura_anterior.name):
                    miniatura_anterior.delete(save=False)

            examen_actualizado.save()  # Aquí se regenerará la miniatura si es necesario

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': 'Examen actualizado correctamente',
                    'examen_data': {
                        'id': examen_actualizado.id,
                        'nombre': examen_actualizado.nombre,
                        'fecha': examen_actualizado.fecha.strftime('%Y-%m-%d') if examen_actualizado.fecha else '',
                        'archivo_url': examen_actualizado.archivo.url if examen_actualizado.archivo else '',
                        'miniatura_url': examen_actualizado.miniatura.url if examen_actualizado.miniatura else '',
                    }
                })
            messages.success(request, 'Examen actualizado correctamente.')
            return redirect('repositorio')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            # Para peticiones no-AJAX, mostrar errores
            messages.error(request, 'Por favor corrige los errores en el formulario')

    # Respuesta AJAX - retorna solo el fragmento del formulario
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'repositorio/form_fragmento.html', {
            'form': form,
            'form_action': reverse('editar_examen', args=[examen.id]),
            'form_title': 'Editar Examen',
            'submit_text': 'Actualizar Examen'
        })

    # Respuesta normal - retorna la página completa del repositorio
    return render(request, 'repositorio/repositorio.html', {
        'form': form,
        'examen': examen,
        'universidad': universidad
    })


def eliminar_examen(request, examen_id):
    examen = get_object_or_404(Examen, id=examen_id)
    universidad = examen.universidad

    if not tiene_permiso_profesor_sobre(request.user, universidad):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'No tienes permisos para eliminar este examen'}, status=403)
        messages.error(request, 'No tienes permisos para eliminar este examen.')
        return redirect('repositorio')

    if request.method == 'POST':
        try:
            examen_data = {
                'id': examen.id,
                'nombre': examen.nombre
            }
            examen.delete()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': 'Examen eliminado correctamente',
                    'examen_id': examen_data['id']
                })
            messages.success(request, 'Examen eliminado correctamente.')
            return redirect('repositorio')
        except Exception as e:
            error_msg = f"Error al eliminar el examen: {str(e)}"
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': error_msg}, status=500)
            messages.error(request, error_msg)
            return redirect('repositorio')
    
    # Si no es POST, retornar error
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    return redirect('repositorio')


def obtener_examenes_universidad(request, universidad_id):
    """
    Vista para obtener los exámenes de una universidad específica via AJAX
    """
    universidad = get_object_or_404(Universidad, id=universidad_id)
    
    if not tiene_permiso_profesor_sobre(request.user, universidad):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'No tienes permisos'}, status=403)
        return redirect('repositorio')
    
    examenes = Examen.objects.filter(universidad=universidad).order_by('-fecha', '-id')
    
    examenes_data = []
    for examen in examenes:
        examenes_data.append({
            'id': examen.id,
            'nombre': examen.nombre,
            'fecha': examen.fecha.strftime('%Y-%m-%d') if examen.fecha else '',
            'archivo_url': examen.archivo.url if examen.archivo else '',
            'miniatura_url': examen.miniatura.url if examen.miniatura else '',
        })
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'examenes': examenes_data,
            'universidad': {
                'id': universidad.id,
                'nombre': universidad.nombre_universidad
            }
        })
    
    return redirect('repositorio')