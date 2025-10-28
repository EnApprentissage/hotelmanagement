from django import forms
from .models import Facture

class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = [
            'client', 'reservation', 'commande_resto', 'commande_bar',
            'montant_total', 'statut', 'notes'
        ]
        labels = {
            'client': "Client",
            'reservation': "Réservation (optionnelle)",
            'commande_resto': "Commande restaurant (optionnelle)",
            'commande_bar': "Commande bar (optionnelle)",
            'montant_total': "Montant total",
            'statut': "Statut de la facture",
            'notes': "Notes",
        }
        widgets = {
            'statut': forms.Select(),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ex : consommations spécifiques'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        reservation = cleaned_data.get('reservation')
        commande_resto = cleaned_data.get('commande_resto')
        commande_bar = cleaned_data.get('commande_bar')

        if not reservation and not commande_resto and not commande_bar:
            raise forms.ValidationError(
                "Vous devez lier la facture à une réservation, une commande restaurant ou une commande bar."
            )
        return cleaned_data
