# inventaire/forms.py
from django import forms
from .models import (
    CategorieInventaire, Produit, MouvementStock,
    DemandeReapprovisionnement, InventairePhysique,
    DotationChambre, Signalement
)

class CategorieInventaireForm(forms.ModelForm):
    class Meta:
        model = CategorieInventaire
        fields = '__all__'

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = '__all__'

class MouvementStockForm(forms.ModelForm):
    class Meta:
        model = MouvementStock
        fields = '__all__'

class DemandeReapproForm(forms.ModelForm):
    class Meta:
        model = DemandeReapprovisionnement
        fields = '__all__'

class InventairePhysiqueForm(forms.ModelForm):
    class Meta:
        model = InventairePhysique
        fields = '__all__'

class DotationChambreForm(forms.ModelForm):
    class Meta:
        model = DotationChambre
        fields = '__all__'

class SignalementForm(forms.ModelForm):
    class Meta:
        model = Signalement
        fields = '__all__'
