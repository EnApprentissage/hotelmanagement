# reservations/forms.py
from django import forms
from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            'client', 'chambre', 'date_arrivee', 'date_depart',
            'nombre_adultes', 'nombre_enfants', 'type_reservation',
            'prix_par_nuit', 'acompte', 'demandes_speciales', 'notes'
        ]
        labels = {
            'client': "Client",
            'chambre': "Chambre",
            'date_arrivee': "Date d'arrivée",
            'date_depart': "Date de départ",
            'nombre_adultes': "Nombre d'adultes",
            'nombre_enfants': "Nombre d'enfants",
            'type_reservation': "Type de réservation",
            'prix_par_nuit': "Prix par nuit",
            'acompte': "Acompte",
            'demandes_speciales': "Demandes spéciales",
            'notes': "Notes internes",
        }
        widgets = {
            'date_arrivee': forms.DateInput(attrs={'type': 'date'}),
            'date_depart': forms.DateInput(attrs={'type': 'date'}),
            'demandes_speciales': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ex : chambre côté piscine, lit bébé...'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Notes internes pour le personnel'}),
            'type_reservation': forms.Select(),
        }

    def clean(self):
        cleaned_data = super().clean()
        arrivee = cleaned_data.get('date_arrivee')
        depart = cleaned_data.get('date_depart')
        adultes = cleaned_data.get('nombre_adultes', 0)
        enfants = cleaned_data.get('nombre_enfants', 0)
        chambre = cleaned_data.get('chambre')

        # Vérifie que la date de départ est après la date d'arrivée
        if arrivee and depart and depart <= arrivee:
            raise forms.ValidationError("La date de départ doit être après la date d'arrivée.")

        # Vérifie la capacité de la chambre
        if chambre:
            total_personnes = adultes + enfants
            capacite_totale = chambre.type_chambre.capacite_adultes + chambre.type_chambre.capacite_enfants
            if total_personnes > capacite_totale:
                raise forms.ValidationError(
                    f"Cette chambre ne peut accueillir que {chambre.type_chambre.capacite_adultes} adultes "
                    f"et {chambre.type_chambre.capacite_enfants} enfants (total {capacite_totale} personnes)."
                )

        return cleaned_data
