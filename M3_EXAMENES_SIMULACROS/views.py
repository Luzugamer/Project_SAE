from django.shortcuts import render
from django.http import HttpResponse

def test_simulacro(request):
    return HttpResponse("Vista de prueba del módulo de simulacros y evaluaciones.")

def menu_simulacros(request):
    return render(request, "M3_EXAMENES_SIMULACROS/menu_simulacros.html")

def simulacro_individual(request):
    return render(request, "M3_EXAMENES_SIMULACROS/simulacro_individual.html")

def simulacro_grupal(request):
    return render(request, "M3_EXAMENES_SIMULACROS/simulacro_grupal.html")

def resultados(request):
    return render(request, "M3_EXAMENES_SIMULACROS/resultados.html")

