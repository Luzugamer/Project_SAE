from django.shortcuts import render

def accesibilidad_index(request):
    return render(request, 'accesibilidad/index.html')