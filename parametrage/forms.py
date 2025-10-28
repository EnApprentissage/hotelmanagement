from django import forms
from .models import GlobalVariables

class GlobalVariablesForm(forms.ModelForm):
    class Meta:
        model = GlobalVariables
        fields = ['group', 'cle', 'valeur', 'description']
        labels = {
            'group': 'Groupe',
            'cle': 'Clé',
            'valeur': 'Valeur',
            'description': 'Description',
        }
        widgets = {
            'group': forms.TextInput(attrs={'placeholder': 'ex: hotel, paiement, taxe'}),
            'cle': forms.TextInput(attrs={'placeholder': 'ex: nom_hotel, taux_tva'}),
            'valeur': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }
