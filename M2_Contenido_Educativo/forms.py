from django import forms
from .models import Universidad, Examen, PAISES_CHOICES

class UniversidadForm(forms.ModelForm):
    pais = forms.ChoiceField(
        choices=PAISES_CHOICES,
        widget=forms.Select(attrs={
            'class': 'select-pais',
            'data-live-search': 'true',
            'title': 'Seleccione un país...'
        })
    )
    
    class Meta:
        model = Universidad
        fields = ['nombre', 'pais', 'logo', 'especialidad', 'tipo_solucionario']
        widgets = {
            'logo': forms.ClearableFileInput(attrs={'accept': 'image/*'})
        }

    def clean_logo(self):
        logo = self.cleaned_data.get('logo', False)
        if logo:
            if logo.size > 2 * 1024 * 1024:  # 2MB
                raise forms.ValidationError("El logo no debe superar los 2MB")
            return logo
        return self.instance.logo if self.instance else None

class ExamenForm(forms.ModelForm):
    class Meta:
        model = Examen
        fields = ['nombre', 'fecha', 'archivo']