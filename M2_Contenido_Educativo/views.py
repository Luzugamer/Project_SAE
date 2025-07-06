from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import Universidad, Examen
from .forms import UniversidadForm, ExamenForm
from django.core.files.base import ContentFile
import base64
import uuid


def vista_repositorio(request):
    universidades = Universidad.objects.all()
    return render(request, 'repositorio/repositorio.html', {'universidades': universidades})

def add_universidad(request):
    if request.method == 'POST':
        form = UniversidadForm(request.POST, request.FILES)
        if form.is_valid():
            # Para previsualización AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and not request.POST.get('confirm_save'):
                logo_url = ''
                if 'logo' in request.FILES:
                    logo = request.FILES['logo']
                    logo.seek(0)
                    logo_url = 'data:' + logo.content_type + ';base64,' + base64.b64encode(logo.read()).decode('utf-8')
                
                return JsonResponse({
                    'success': True,
                    'nombre': form.cleaned_data['nombre'],
                    'pais': form.cleaned_data['pais'],
                    'especialidad': form.cleaned_data['especialidad'],
                    'tipo_solucionario': dict(form.fields['tipo_solucionario'].choices).get(form.cleaned_data['tipo_solucionario']),
                    'logo_url': logo_url,
                    'preview': True
                })
            
            # Guardado definitivo
            universidad = form.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'redirect': not request.POST.get('add_another'),
                    'add_another': request.POST.get('add_another') == 'true'
                })
            else:
                if request.POST.get('add_another') == 'true':
                    return redirect('add_universidad')
                return redirect('repositorio')
        
        # Manejo de errores
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'errors': form.errors
            }, status=400)
        
        return render(request, 'repositorio/add_universidad.html', {'form': form})
    
    # GET request
    form = UniversidadForm()
    return render(request, 'repositorio/add_universidad.html', {'form': form})

def editar_universidad(request, universidad_id):
    universidad = get_object_or_404(Universidad, id=universidad_id)
    
    if request.method == 'POST':
        form = UniversidadForm(request.POST, request.FILES, instance=universidad)
        if form.is_valid():
            # Para solicitudes AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Si NO es confirmación de guardado, es previsualización
                if not request.POST.get('confirm_save'):
                    # Obtener URL del logo
                    logo_url = ''
                    if 'logo' in request.FILES:
                        logo = request.FILES['logo']
                        logo.seek(0)
                        logo_url = 'data:' + logo.content_type + ';base64,' + base64.b64encode(logo.read()).decode('utf-8')
                    elif universidad.logo and not form.cleaned_data.get('logo-clear'):
                        logo_url = universidad.logo.url
                    
                    return JsonResponse({
                        'success': True,
                        'nombre': form.cleaned_data['nombre'],
                        'pais': form.cleaned_data['pais'],
                        'especialidad': form.cleaned_data['especialidad'],
                        'tipo_solucionario': dict(form.fields['tipo_solucionario'].choices).get(form.cleaned_data['tipo_solucionario']),
                        'logo_url': logo_url,
                        'preview': True,
                        'is_edit': True
                    })
                
                # Si es confirmación de guardado, guardar definitivamente
                universidad = form.save()
                return JsonResponse({
                    'success': True,
                    'redirect': True,
                    'message': 'Universidad actualizada correctamente'
                })
            
            # Para envío tradicional de formulario (no AJAX)
            universidad = form.save()
            messages.success(request, 'Universidad actualizada correctamente')
            return redirect('repositorio')
        
        # Manejo de errores para AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'errors': form.errors
            }, status=400)
        
        # Para errores en envío tradicional
        return render(request, 'repositorio/add_universidad.html', {
            'form': form,
            'universidad': universidad
        })
    
    # GET request
    form = UniversidadForm(instance=universidad)
    return render(request, 'repositorio/add_universidad.html', {
        'form': form,
        'universidad': universidad
    })

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
            examen = Examen.objects.create(
                universidad=universidad,
                nombre=nombre,
                fecha=fecha,
                archivo=archivo
            )
            examen.save()  # Esto generará automáticamente la miniatura
    return redirect('repositorio')


def eliminar_universidad(request, universidad_id):
    universidad = get_object_or_404(Universidad, id=universidad_id)
    try:
        universidad.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Repositorio eliminado correctamente'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


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