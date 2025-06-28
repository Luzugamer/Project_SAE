from django.http import HttpResponse

def modo_nocturno_inicio(request):
    return HttpResponse("Modo nocturno funcionando correctamente.")
