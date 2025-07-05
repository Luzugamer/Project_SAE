
from django.http import HttpResponse

def test_generador(request):
    return HttpResponse("Vista de prueba del generador de preguntas por IA.")

from django.http import JsonResponse
from M3_GENERADOR_EXAMENES.ai_services.ai_client import generar_respuesta

def generar_pregunta(request):
    if request.method == "POST":
        tema = request.POST.get("tema", "")
        if not tema:
            return JsonResponse({"error": "Tema no especificado"}, status=400)
        
        prompt = f"Genera una pregunta tipo opción múltiple sobre el siguiente tema: {tema}"
        respuesta = generar_respuesta(prompt)
        return JsonResponse({"pregunta_generada": respuesta})
    
    return JsonResponse({"error": "Método no permitido"}, status=405)