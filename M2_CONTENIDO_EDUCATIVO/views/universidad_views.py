from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse

from .base import tiene_permiso_profesor_sobre
from M2_CONTENIDO_EDUCATIVO.models import Universidad
from M2_CONTENIDO_EDUCATIVO.forms import UniversidadForm 
from Login.models import UsuarioRol


def add_universidad(request):
    if not request.user.is_authenticated or not UsuarioRol.objects.filter(usuario=request.user, rol__nombre_rol='profesor').exists():
        return redirect('repositorio')

    from M2_CONTENIDO_EDUCATIVO.forms import UniversidadForm  # Unico Form

    if request.method == 'POST':
        form = UniversidadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            universidad = form.save(commit=False)
            universidad.profesor_creador = request.user
            universidad.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                if request.POST.get('confirm_save') == 'true':
                    return JsonResponse({
                        'success': True,
                        'redirect': True,
                        'add_another': request.POST.get('add_another') == 'true'
                    })

                return JsonResponse({
                    'success': True,
                    'preview': True,
                    'is_edit': False,
                    'nombre': universidad.nombre,
                    'pais': universidad.get_pais_display(),
                    'tipo_solucionario': universidad.get_tipo_solucionario_display(),
                    'logo_url': universidad.logo.url if universidad.logo else '',
                })

            return redirect('repositorio')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    # Valores iniciales
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

    # Elegimos el formulario adecuado según el tipo de solucionario
    from M2_CONTENIDO_EDUCATIVO.forms import UniversidadAdmisionForm, SolucionarioGeneralForm
    FormClass = UniversidadAdmisionForm if universidad.tipo_solucionario == 'admision' else SolucionarioGeneralForm

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=universidad, user=request.user)
        if form.is_valid():
            universidad = form.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Actualización exitosa'})

            messages.success(request, 'Repositorio actualizado correctamente')
            return redirect('repositorio')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    else:
        form = FormClass(instance=universidad, user=request.user)

    return render(request, 'repositorio/add_universidad.html', {
        'form': form,
        'universidad': universidad,
        'editing': True
    })


def eliminar_universidad(request, universidad_id):
    universidad = get_object_or_404(Universidad, id=universidad_id)

    if not tiene_permiso_profesor_sobre(request.user, universidad):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para eliminar este repositorio.'
            }, status=403)
        messages.error(request, 'No tienes permisos para eliminar este repositorio.')
        return redirect('repositorio')

    try:
        universidad.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Repositorio eliminado correctamente.',
                'redirect_url': reverse('repositorio')
            })
        messages.success(request, 'Repositorio eliminado correctamente.')
        return redirect('repositorio')
    except Exception as e:
        error_msg = f"Error al eliminar el repositorio: {str(e)}"
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg}, status=500)
        messages.error(request, error_msg)
        