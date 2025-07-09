from django import forms

class PreguntaForm(forms.Form):
    pregunta = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Escribe tu pregunta o problema matemático aquí...',
            'rows': 4,
            'required': True
        }),
        max_length=2000,
        label='Tu pregunta'
    )
    
    nivel = forms.ChoiceField(
        choices=[
            ('', 'Selecciona tu nivel'),
            ('secundaria', '5to Secundaria'),
            ('universitario', 'Universitario')
        ],
        required=False,
        label='Nivel académico'
    )
    
    def clean_pregunta(self):
        pregunta = self.cleaned_data.get('pregunta')
        if len(pregunta.strip()) < 10:
            raise forms.ValidationError("La pregunta debe tener al menos 10 caracteres.")
        return pregunta