from django import forms
from .models import CategorieMenu, ProduitMenu, Table, Commande, CommandeItem

class CategorieMenuForm(forms.ModelForm):
    class Meta:
        model = CategorieMenu
        fields = '__all__'

class ProduitMenuForm(forms.ModelForm):
    class Meta:
        model = ProduitMenu
        fields = '__all__'

class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = '__all__'

class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = '__all__'

class CommandeItemForm(forms.ModelForm):
    class Meta:
        model = CommandeItem
        fields = '__all__'
