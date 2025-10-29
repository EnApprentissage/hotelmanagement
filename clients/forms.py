# clients/forms.py
from django import forms
from .models import Client, HistoriqueClient
import re

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'civilite', 'nom', 'prenom', 'date_naissance', 'nationalite',
            'adresse', 'ville', 'pays', 'phone', 'email',
            'type_piece', 'numero_piece', 'piece_identite',
            'type_chambre_prefere', 'preferences_speciales', 'notes'
        ]
        labels = {
            'civilite': "Civilité",
            'nom': "Nom",
            'prenom': "Prénom",
            'date_naissance': "Date de naissance",
            'nationalite': "Nationalité",
            'adresse': "Adresse",
            'ville': "Ville",
            'pays': "Pays",
            'phone': "Téléphone",
            'email': "Email",
            'type_piece': "Type de pièce d'identité",
            'numero_piece': "Numéro de la pièce",
            'piece_identite': "Pièce d'identité",
            'type_chambre_prefere': "Type de chambre préféré",
            'preferences_speciales': "Préférences spéciales",
            'notes': "Notes",
        }
        widgets = {
            'civilite': forms.Select(choices=Client.CIVILITE_CHOICES, attrs={'class': 'form-select form-select-sm'}),
            'nom': forms.TextInput(attrs={'placeholder': 'Nom', 'class': 'form-control form-control-sm'}),
            'prenom': forms.TextInput(attrs={'placeholder': 'Prénom', 'class': 'form-control form-control-sm'}),
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
            'nationalite': forms.TextInput(attrs={'placeholder': 'Nationalité', 'class': 'form-control form-control-sm'}),
            'adresse': forms.Textarea(attrs={'rows': 2, 'class': 'form-control form-control-sm'}),
            'ville': forms.TextInput(attrs={'placeholder': 'Ville', 'class': 'form-control form-control-sm'}),
            'pays': forms.TextInput(attrs={'placeholder': 'Pays', 'class': 'form-control form-control-sm'}),
            'phone': forms.TextInput(attrs={'placeholder': '+243...', 'class': 'form-control form-control-sm'}),
            'email': forms.EmailInput(attrs={'placeholder': 'email@example.com', 'class': 'form-control form-control-sm'}),
            'type_piece': forms.TextInput(attrs={'placeholder': 'Passeport, CNI...', 'class': 'form-control form-control-sm'}),
            'numero_piece': forms.TextInput(attrs={'placeholder': 'Numéro pièce', 'class': 'form-control form-control-sm'}),
            'piece_identite': forms.FileInput(attrs={'class': 'form-control form-control-sm'}),
            'type_chambre_prefere': forms.TextInput(attrs={'placeholder': 'Ex : Suite, Simple', 'class': 'form-control form-control-sm'}),
            'preferences_speciales': forms.Textarea(attrs={'rows': 2, 'class': 'form-control form-control-sm'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control form-control-sm'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Client.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not re.match(r'^\+\d{6,15}$', phone):
            raise forms.ValidationError("Le numéro doit être au format international (+243...) et contenir uniquement des chiffres.")
        return phone


class HistoriqueClientForm(forms.ModelForm):
    class Meta:
        model = HistoriqueClient
        fields = ['type', 'description', 'montant']
        labels = {
            'type': "Type d'historique",
            'description': "Description",
            'montant': "Montant (si applicable)",
        }
        widgets = {
            'type': forms.Select(choices=HistoriqueClient.TYPE_CHOICES, attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        type_choice = cleaned_data.get('type')
        montant = cleaned_data.get('montant')

        # Montant obligatoire pour les séjours
        if type_choice == 'sejour' and (montant is None or montant <= 0):
            self.add_error('montant', "Le montant est obligatoire pour les séjours.")
        return cleaned_data
