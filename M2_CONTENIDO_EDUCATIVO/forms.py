from django import forms
from .models import Universidad, Examen, PAISES_CHOICES
from Login.models import UsuarioRol
import re

# ========== FORMULARIO 1: Repositorio de Admisión ==========
class UniversidadAdmisionForm(forms.ModelForm):
    pais = forms.ChoiceField(
        choices=PAISES_CHOICES,
        widget=forms.Select(attrs={
            'class': 'select-pais',
            'data-live-search': 'true',
            'title': 'Seleccione un país...'
        }),
        required=True
    )

    class Meta:
        model = Universidad
        fields = [
            'nombre', 'pais', 'logo',
            'codigo_modular', 'institucion_educativa',
            'departamento', 'provincia', 'distrito'
        ]

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')

        if not nombre:
            self.add_error('nombre', 'El nombre es obligatorio.')
        elif not any(x in nombre.lower() for x in ['universidad', 'instituto']):
            self.add_error('nombre', "Ejemplo sugerido: 'Universidad Nacional de Ingeniería'")

        if not cleaned_data.get('logo'):
            self.add_error('logo', 'El logo es obligatorio.')

        return cleaned_data

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo and logo.size > 2 * 1024 * 1024:
            raise forms.ValidationError("El logo no debe superar los 2MB.")
        return logo

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            if UsuarioRol.objects.filter(usuario=user, rol__nombre_rol='profesor').exists():
                self.fields['codigo_modular'].initial = user.codigo_modular
                self.fields['institucion_educativa'].initial = user.institucion_educativa
                self.fields['departamento'].initial = user.departamento
                self.fields['provincia'].initial = user.provincia
                self.fields['distrito'].initial = user.distrito


# ========== FORMULARIO 2: Solucionario de Ejercicios u Otro ==========
class SolucionarioGeneralForm(forms.ModelForm):
    class Meta:
        model = Universidad
        fields = [
            'nombre', 'curso', 'logo',
            'codigo_modular', 'institucion_educativa',
            'departamento', 'provincia', 'distrito'
        ]

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        curso = cleaned_data.get('curso')

        if not curso:
            self.add_error('curso', 'El campo curso es obligatorio.')

        if not nombre:
            self.add_error('nombre', 'El nombre es obligatorio.')
        elif not re.match(r'^.+\s-\s.+$', nombre.strip()):
            self.add_error('nombre', 'Formato requerido: "Curso - Tema" (ej: Matemática - Funciones)')

        return cleaned_data

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo and logo.size > 2 * 1024 * 1024:
            raise forms.ValidationError("El logo no debe superar los 2MB.")
        return logo

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            if UsuarioRol.objects.filter(usuario=user, rol__nombre_rol='profesor').exists():
                self.fields['codigo_modular'].initial = user.codigo_modular
                self.fields['institucion_educativa'].initial = user.institucion_educativa
                self.fields['departamento'].initial = user.departamento
                self.fields['provincia'].initial = user.provincia
                self.fields['distrito'].initial = user.distrito


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
