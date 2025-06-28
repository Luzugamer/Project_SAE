from __future__ import annotations
from django import forms

class AjustesAccesibilidadForm(forms.Form):
    TAMANOS_FUENTE = [
        ('pequeno', 'Pequeño'),
        ('mediano', 'Mediano'),
        ('grande', 'Grande'),
    ]
    tamano_fuente = forms.ChoiceField(choices=TAMANOS_FUENTE, label="Tamaño de fuente")
    alto_contraste = forms.BooleanField(required=False, label="Alto contraste")
