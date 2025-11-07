# staff/forms.py
from django import forms
from .models import Employe, Planning, Pointage, Conge, Evaluation, Incident

# ============================
# Formulaire Employé
# ============================

class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = [
            'nom',
            'prenom',
            'date_naissance',
            'lieu_naissance',
            'nationalite',
            'etat_civil',
            'adresse',
            'ville',
            'pays',
            'phone',
            'email',
            'poste',
            'departement',
            'date_embauche',
            'salaire',
            'cv',
            'contrat',
            'photo',
            'contact_urgence_nom',
            'contact_urgence_phone',
            'contact_urgence_relation',
        ]

        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'lieu_naissance': forms.TextInput(attrs={'class': 'form-control'}),
            'nationalite': forms.TextInput(attrs={'class': 'form-control'}),
            'etat_civil': forms.Select(attrs={'class': 'form-select'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'poste': forms.TextInput(attrs={'class': 'form-control'}),
            'departement': forms.TextInput(attrs={'class': 'form-control'}),
            'date_embauche': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'salaire': forms.NumberInput(attrs={'class': 'form-control'}),
            'cv': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'contrat': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'contact_urgence_nom': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_urgence_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_urgence_relation': forms.TextInput(attrs={'class': 'form-control'}),
        }

    # Exemple de validation personnalisée
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise forms.ValidationError("Le numéro de téléphone doit contenir uniquement des chiffres.")
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
