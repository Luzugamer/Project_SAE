from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from M2_CONTENIDO_EDUCATIVO.models import Universidad

def vista_repositorio(request):
    queryset = Universidad.objects.all().select_related('profesor_creador')
    
    if request.user.is_authenticated and getattr(request.user, 'rol', None) == 'profesor':
        queryset = queryset.filter(
            codigo_modular=request.user.codigo_modular,
            institucion_educativa=request.user.institucion_educativa
        )
    
    institucion_filter = request.GET.get('institucion')
    tipo_filter = request.GET.get('tipo_solucionario')
    
    if institucion_filter or tipo_filter:
        filtro = {}
        if institucion_filter:
            queryset = queryset.filter(institucion_educativa__iexact=institucion_filter)
        if tipo_filter:
            queryset = queryset.filter(tipo_solucionario=tipo_filter)
        queryset = queryset.filter(**filtro)

    context = {
        'universidades': queryset,
        'instituciones': Universidad.objects.exclude(institucion_educativa__isnull=True)
                             .values_list('institucion_educativa', flat=True)
                             .distinct(),
        'tipos_solucionario': Universidad.TIPO_SOLUCIONARIO_CHOICES
    }
    return render(request, 'repositorio/repositorio.html', context)

def vista_examenes_universidad(request, universidad_id):
    #no util, pero funciona.
    return redirect('repositorio')

def examenes_ajax(request, universidad_id):
    universidad = get_object_or_404(Universidad, id=universidad_id)
    examenes = universidad.examenes.all()

    examenes_data = [
        {
            'id': examen.id,
            'nombre': examen.nombre,
            'fecha': str(examen.fecha),
            'archivo': examen.archivo.url if examen.archivo else ''
        }
        for examen in examenes
    ]

    return JsonResponse({'examenes': examenes_data})