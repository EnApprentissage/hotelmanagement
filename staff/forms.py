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
            'user', 'nom', 'prenom', 'date_naissance', 'lieu_naissance',
            'nationalite', 'etat_civil', 'adresse', 'ville', 'pays',
            'phone', 'email', 'poste', 'departement', 'date_embauche',
            'salaire', 'cv', 'contrat', 'photo',
            'contact_urgence_nom', 'contact_urgence_phone', 'contact_urgence_relation'
        ]
        labels = {
            'user': "Compte utilisateur",
            'nom': "Nom",
            'prenom': "Prénom",
            'date_naissance': "Date de naissance",
            'lieu_naissance': "Lieu de naissance",
            'nationalite': "Nationalité",
            'etat_civil': "État civil",
            'adresse': "Adresse",
            'ville': "Ville",
            'pays': "Pays",
            'phone': "Téléphone",
            'email': "Email",
            'poste': "Poste",
            'departement': "Département",
            'date_embauche': "Date d'embauche",
            'salaire': "Salaire",
            'cv': "CV",
            'contrat': "Contrat",
            'photo': "Photo",
            'contact_urgence_nom': "Nom contact d'urgence",
            'contact_urgence_phone': "Téléphone contact d'urgence",
            'contact_urgence_relation': "Relation contact d'urgence",
        }
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'date_embauche': forms.DateInput(attrs={'type': 'date'}),
            'etat_civil': forms.Select(),
            'adresse': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Adresse complète'}),
            'cv': forms.FileInput(),
            'contrat': forms.FileInput(),
            'photo': forms.FileInput(),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Employe.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.startswith('+'):
            raise forms.ValidationError("Le numéro doit commencer par + (ex: +243).")
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
