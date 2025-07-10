from django.http import HttpResponse
from django.shortcuts import render
from .models import ArchivoEscaneado
from M3_ESCANER_REPOSITORIO.extractors.pdf_extractor import extraer_texto_pdf
from M3_ESCANER_REPOSITORIO.extractors.preprocessor import limpiar_texto
import os

def test_escaneo(request):
    return HttpResponse("Vista de prueba del módulo de escaneo de archivos PDF.")


def escanear_archivo(request):
    if request.method == 'POST' and request.FILES.get('archivo_pdf'):
        archivo = request.FILES['archivo_pdf']
        nuevo_archivo = ArchivoEscaneado.objects.create(
            nombre_archivo=archivo.name,
            archivo_pdf=archivo
        )

        ruta_absoluta = nuevo_archivo.archivo_pdf.path
        texto_crudo = extraer_texto_pdf(ruta_absoluta)
        texto_limpio = limpiar_texto(texto_crudo)

        nuevo_archivo.texto_extraido = texto_limpio
        nuevo_archivo.save()

        return render(request, 'M3_ESCANER_REPOSITORIO/resultado_escaneo.html', {
            'archivo': nuevo_archivo,
            'texto': texto_limpio
        })

    return render(request, 'M3_ESCANER_REPOSITORIO/subir_archivo.html')