from django import forms
from .models import Universidad, Examen

class UniversidadForm(forms.ModelForm):
    class Meta:
        model = Universidad
        fields = ['nombre', 'pais', 'logo', 'especialidad', 'tipo_solucionario']

class ExamenForm(forms.ModelForm):
   class Meta:
        model = Examen
        fields = ['nombre', 'fecha', 'archivo']