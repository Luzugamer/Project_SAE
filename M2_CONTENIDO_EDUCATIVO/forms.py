from django import forms
from .models import Universidad, Examen, PAISES_CHOICES
from Login.models import UsuarioRol
import re

class UniversidadForm(forms.ModelForm):
    pais = forms.ChoiceField(
        choices=PAISES_CHOICES,
        widget=forms.Select(attrs={
            'class': 'select-pais',
            'data-live-search': 'true',
            'title': 'Seleccione un país...'
        }),
        required=False
    )

    class Meta:
        model = Universidad
        fields = [
            'tipo_solucionario', 'nombre', 'logo',
            'pais', 'carrera', 'curso', 'nivel',
            'codigo_modular', 'institucion_educativa',
            'departamento', 'provincia', 'distrito'
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated: #rellenado automatico segun los datos de usuario
            if UsuarioRol.objects.filter(usuario=user, rol__nombre_rol='profesor').exists():
                self.fields['codigo_modular'].initial = user.codigo_modular
                self.fields['institucion_educativa'].initial = user.institucion_educativa
                self.fields['departamento'].initial = user.departamento
                self.fields['provincia'].initial = user.provincia
                self.fields['distrito'].initial = user.distrito

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo_solucionario')
        nombre = cleaned_data.get('nombre')

        # Validación general del nombre
        if not nombre:
            self.add_error('nombre', 'El nombre es obligatorio.')

        if tipo == 'admision':
            if not cleaned_data.get('pais'):
                self.add_error('pais', "El campo 'País' es obligatorio para exámenes de admisión.")
            if not cleaned_data.get('carrera'):
                self.add_error('carrera', "El campo 'Carrera' es obligatorio para exámenes de admisión.")
            if nombre and not any(x in nombre.lower() for x in ['universidad', 'instituto']):
                self.add_error('nombre', "Ejemplo sugerido: 'Universidad Nacional de Ingeniería'.")

        elif tipo == 'ejercicios':
            if not cleaned_data.get('curso'):
                self.add_error('curso', "El campo 'Curso' es obligatorio para solucionarios de ejercicios.")
            if not cleaned_data.get('nivel'):
                self.add_error('nivel', "El campo 'Nivel Académico' es obligatorio para solucionarios de ejercicios.")
            if nombre and not re.match(r'^.+\s-\s.+$', nombre.strip()):
                self.add_error('nombre', 'Formato requerido: "Curso - Tema" (ej: Matemática - Funciones)')

        # Validación común para tipos admision y ejercicios
        if tipo in ['admision', 'ejercicios', 'otro']:
            if not cleaned_data.get('logo'):
                self.add_error('logo', 'El logo es obligatorio.')

        return cleaned_data

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo and logo.size > 2 * 1024 * 1024:
            raise forms.ValidationError("El logo no debe superar los 2MB.")
        return logo

class ExamenForm(forms.ModelForm):
    class Meta:
        model = Examen
        fields = ['nombre', 'fecha', 'archivo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            if not archivo.content_type == 'application/pdf':
                raise forms.ValidationError("El archivo debe ser un documento PDF.")
            if archivo.size > 10 * 1024 * 1024:
                raise forms.ValidationError("El archivo no debe superar los 10MB.")
        return archivo