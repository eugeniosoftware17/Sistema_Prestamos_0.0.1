from django import forms
from .models import ConfiguracionImpresion

class ConfiguracionImpresionForm(forms.ModelForm):
    """
    Formulario para editar la configuración de impresión.
    """
    class Meta:
        model = ConfiguracionImpresion
        fields = [
            'logo', 
            'pie_de_pagina', 
            'mostrar_seccion_garante', 
            'mostrar_tabla_amortizacion'
        ]
        widgets = {
            'pie_de_pagina': forms.Textarea(attrs={'rows': 3}),
        }
