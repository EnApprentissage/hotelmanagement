# staff/forms.py
import re
from django import forms
from .models import Employe, Planning, Pointage, Conge, Evaluation, Incident

# ============================
# Formulaire Employé
# ============================

class EmployeForm(forms.ModelForm):

    # ON FORCE les bons ChoiceField avec Select pour les champs à choices
    sexe = forms.ChoiceField(
        choices=Employe._meta.get_field('sexe').choices,  # = [('M', 'Masculin'), ('F', 'Féminin')]
        widget=forms.Select(attrs={'class': 'form-select form-control-sm'}),
        label="Sexe"
    )

    etat_civil = forms.ChoiceField(
        choices=Employe.ETAT_CIVIL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-control-sm'}),
        label="État civil"
    )

    class Meta:
        model = Employe
        fields = [
            'nom', 'prenom', 'date_naissance', 'lieu_naissance', 'nationalite',
            'sexe', 'etat_civil', 'adresse', 'ville', 'pays', 'phone', 'email',
            'poste', 'departement', 'date_embauche', 'salaire',
            'cv', 'contrat', 'photo',
            'contact_urgence_nom', 'contact_urgence_phone', 'contact_urgence_relation',
        ]

        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': "Nom de l'employé"}),
            'prenom': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': "Prénom de l'employé"}),
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
            'lieu_naissance': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': "Lieu de naissance"}),
            'nationalite': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': "Nationalité"}),
            # sexe et etat_civil sont gérés plus haut avec ChoiceField → on les enlève du widgets
            'adresse': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3, 'placeholder': "Adresse de l'employé"}),
            'ville': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': "Ville"}),
            'pays': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': "Pays"}),
            'phone': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': "Numéro de téléphone"}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-sm', 'placeholder': "Email"}),
            'poste': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': "Poste"}),
            'departement': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': "Département"}),
            'date_embauche': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
            'salaire': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'cv': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm'}),
            'contrat': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm'}),
            'contact_urgence_nom': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': "Nom contact d'urgence"}),
            'contact_urgence_phone': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': "Téléphone contact d'urgence"}),
            'contact_urgence_relation': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': "Relation"}),
        }

    # Tes validations personnalisées (inchangées)
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        phone_digits = re.sub(r'[^\d+]', '', phone)
        digits_only = re.sub(r'[^\d]', '', phone_digits)
        if len(digits_only) < 8:
            raise forms.ValidationError("Le numéro de téléphone doit contenir au moins 8 chiffres.")
        return phone_digits

    def clean_contact_urgence_phone(self):
        phone = self.cleaned_data.get('contact_urgence_phone', '')
        if phone:
            phone_digits = re.sub(r'[^\d+]', '', phone)
            digits_only = re.sub(r'[^\d]', '', phone_digits)
            if len(digits_only) < 10:
                raise forms.ValidationError("Le numéro de téléphone doit contenir au moins 10 chiffres.")
            return phone_digits
        return phone
    
# ============================
# Formulaire Planning
# ============================
class PlanningForm(forms.ModelForm):
    class Meta:
        model = Planning
        fields = ['employe', 'date', 'periode', 'heure_debut', 'heure_fin', 'poste_assigne', 'notes']
        labels = {
            'employe': "Employé",
            'date': "Date",
            'periode': "Période",
            'heure_debut': "Heure de début",
            'heure_fin': "Heure de fin",
            'poste_assigne': "Poste assigné",
            'notes': "Notes",
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'heure_debut': forms.TimeInput(attrs={'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'type': 'time'}),
            'periode': forms.Select(),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Informations supplémentaires'}),
        }

# ============================
# Formulaire Pointage
# ============================
class PointageForm(forms.ModelForm):
    class Meta:
        model = Pointage
        fields = ['employe', 'date', 'heure_arrivee', 'heure_depart', 'notes']
        labels = {
            'employe': "Employé",
            'date': "Date",
            'heure_arrivee': "Heure d'arrivée",
            'heure_depart': "Heure de départ",
            'notes': "Notes",
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'heure_arrivee': forms.TimeInput(attrs={'type': 'time'}),
            'heure_depart': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

# ============================
# Formulaire Congé
# ============================
class CongeForm(forms.ModelForm):
    class Meta:
        model = Conge
        fields = ['employe', 'type_conge', 'date_debut', 'date_fin', 'nombre_jours', 'motif', 'statut']
        labels = {
            'employe': "Employé",
            'type_conge': "Type de congé",
            'date_debut': "Date de début",
            'date_fin': "Date de fin",
            'nombre_jours': "Nombre de jours",
            'motif': "Motif",
            'statut': "Statut",
        }
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'type': 'date'}),
            'type_conge': forms.Select(),
            'statut': forms.Select(),
            'motif': forms.Textarea(attrs={'rows': 3}),
        }

# ============================
# Formulaire Évaluation
# ============================
class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = [
            'employe', 'date_evaluation', 'periode_evaluee', 'evaluateur',
            'objectifs', 'realisations', 'points_forts', 'points_amelioration',
            'note_globale', 'commentaires'
        ]
        labels = {
            'employe': "Employé",
            'date_evaluation': "Date de l'évaluation",
            'periode_evaluee': "Période évaluée",
            'evaluateur': "Évaluateur",
            'objectifs': "Objectifs",
            'realisations': "Réalisations",
            'points_forts': "Points forts",
            'points_amelioration': "Points à améliorer",
            'note_globale': "Note globale",
            'commentaires': "Commentaires",
        }
        widgets = {
            'date_evaluation': forms.DateInput(attrs={'type': 'date'}),
            'objectifs': forms.Textarea(attrs={'rows': 3}),
            'realisations': forms.Textarea(attrs={'rows': 3}),
            'points_forts': forms.Textarea(attrs={'rows': 2}),
            'points_amelioration': forms.Textarea(attrs={'rows': 2}),
            'commentaires': forms.Textarea(attrs={'rows': 2}),
        }

# ============================
# Formulaire Incident
# ============================
class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = [
            'employe', 'date_incident', 'type_incident', 'description',
            'sanction', 'date_sanction', 'signale_par'
        ]
        labels = {
            'employe': "Employé",
            'date_incident': "Date de l'incident",
            'type_incident': "Type d'incident",
            'description': "Description",
            'sanction': "Sanction",
            'date_sanction': "Date de sanction",
            'signale_par': "Signalé par",
        }
        widgets = {
            'date_incident': forms.DateInput(attrs={'type': 'date'}),
            'date_sanction': forms.DateInput(attrs={'type': 'date'}),
            'type_incident': forms.Select(),
            'sanction': forms.Select(),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
