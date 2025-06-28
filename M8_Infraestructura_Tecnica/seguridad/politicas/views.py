from django.views import View
from django.shortcuts import render

class PoliticasPrivacidadView(View):
    def get(self, request):
        return render(request, 'politicas/privacidad.html')

def configuracion(request):
    return render(request, 'politicas/config.html')