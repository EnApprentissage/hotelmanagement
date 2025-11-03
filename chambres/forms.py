# chambres/forms.py
from django import forms
from .models import TypeChambre, Chambre, MaintenanceChambre

class TypeChambreForm(forms.ModelForm):
    class Meta:
        model = TypeChambre
        fields = ['nom', 'description', 'capacite_adultes', 'capacite_enfants', 'superficie', 'prix_base', 'equipements', 'image']

class ChambreForm(forms.ModelForm):
    class Meta:
        model = Chambre
        fields = ['numero', 'type_chambre', 'etage', 'statut', 'description', 'notes_internes', 'date_derniere_maintenance']

class MaintenanceChambreForm(forms.ModelForm):
    class Meta:
        model = MaintenanceChambre
        fields = ['chambre', 'probleme', 'priorite', 'statut', 'date_debut', 'date_fin', 'technicien', 'cout', 'notes']
