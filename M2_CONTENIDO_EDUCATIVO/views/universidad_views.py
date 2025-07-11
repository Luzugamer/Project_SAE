from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse


from .base import tiene_permiso_profesor_sobre
from M2_CONTENIDO_EDUCATIVO.models import Universidad
from M2_CONTENIDO_EDUCATIVO.forms import UniversidadForm 
from M2_CONTENIDO_EDUCATIVO.storage import TempPreviewStorage
from Login.models import UsuarioRol

import uuid
import os

def guardar_logo_temporal(archivo_logo):
    extension = os.path.splitext(archivo_logo.name)[1]
    filename = f"preview_{uuid.uuid4()}{extension}"
    temp_storage = TempPreviewStorage()
    path = temp_storage.save(filename, archivo_logo)
    return temp_storage.url(path)

def add_universidad(request):
    if not request.user.is_authenticated or not UsuarioRol.objects.filter(usuario=request.user, rol__nombre_rol='profesor').exists():
        return redirect('repositorio')

    from M2_CONTENIDO_EDUCATIVO.forms import UniversidadForm

    if request.method == 'POST':
        form = UniversidadForm(request.POST, request.FILES, user=request.user)

        if form.is_valid():
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Previsualización sin guardar en la BD
                if request.POST.get('confirm_save') != 'true':
                    universidad_temp = form.save(commit=False)
                    logo_url = guardar_logo_temporal(request.FILES['logo']) if 'logo' in request.FILES else ''
                    
                    return JsonResponse({
                        'success': True,
                        'preview': True,
                        'is_edit': False,
                        'nombre': universidad_temp.nombre,
                        'pais': universidad_temp.get_pais_display(),
                        'tipo_solucionario': universidad_temp.get_tipo_solucionario_display(),
                        'logo_url': logo_url,
                    })
                

                # Guardado real
                universidad = form.save(commit=False)
                universidad.profesor_creador = request.user
                universidad.save()

                return JsonResponse({
                    'success': True,
                    'redirect': True,
                    'add_another': request.POST.get('add_another') == 'true'
                })

            # Si no es AJAX, comportamiento tradicional (según necesites)
            universidad = form.save(commit=False)
            universidad.profesor_creador = request.user
            universidad.save()
            return redirect('repositorio')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    initial = {
        'codigo_modular': request.user.codigo_modular,
        'institucion_educativa': request.user.institucion_educativa,
        'departamento': request.user.departamento,
        'provincia': request.user.provincia,
        'distrito': request.user.distrito,
    }
    form = UniversidadForm(initial=initial, user=request.user)
    return render(request, 'repositorio/add_universidad.html', {'form': form})

def editar_universidad(request, universidad_id):
    universidad = get_object_or_404(Universidad, id=universidad_id)

    if not tiene_permiso_profesor_sobre(request.user, universidad):
        mensaje = 'No tienes permisos para editar esta universidad.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': mensaje}, status=403)
        messages.error(request, mensaje)
        return redirect('repositorio')

    if request.method == 'POST':
        form = UniversidadForm(request.POST, request.FILES, instance=universidad, user=request.user)

        if form.is_valid():
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Solo guardamos si se confirma
                if request.POST.get('confirm_save') != 'true':
                    universidad_temp = form.save(commit=False)
                    logo_url = guardar_logo_temporal(request.FILES['logo']) if 'logo' in request.FILES else ''

                    return JsonResponse({
                        'success': True,
                        'preview': True,
                        'is_edit': True,
                        'nombre': universidad_temp.nombre,
                        'pais': universidad_temp.get_pais_display(),
                        'tipo_solucionario': universidad_temp.get_tipo_solucionario_display(),
                        'logo_url': logo_url,
                    })


                # Guardado real
                universidad = form.save()
                return JsonResponse({
                    'success': True,
                    'redirect': True,
                })

            # Fallback no-AJAX
            universidad = form.save()
            messages.success(request, 'Repositorio actualizado correctamente')
            return redirect('repositorio')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    else:
        form = UniversidadForm(instance=universidad, user=request.user)

    return render(request, 'repositorio/add_universidad.html', {
        'form': form,
        'universidad': universidad,
        'editing': True
    })



def eliminar_universidad(request, universidad_id):
    universidad = get_object_or_404(Universidad, id=universidad_id)

    if not tiene_permiso_profesor_sobre(request.user, universidad):
        mensaje = 'No tienes permisos para eliminar este repositorio.'
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': mensaje}, status=403)
        messages.error(request, mensaje)
        return redirect('repositorio')

    try:
        universidad.delete()  
        mensaje_ok = 'Repositorio eliminado correctamente.'

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': mensaje_ok,
                'redirect_url': reverse('repositorio')
            })

        messages.success(request, mensaje_ok)
        return redirect('repositorio')

    except Exception as e:
        error_msg = f"Error al eliminar el repositorio: {str(e)}"

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg}, status=500)

        messages.error(request, error_msg)
        return redirect('repositorio')

        