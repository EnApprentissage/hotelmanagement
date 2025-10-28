from django import forms
from .models import SystemConfig, ActionLog, Notification

class SystemConfigForm(forms.ModelForm):
    class Meta:
        model = SystemConfig
        fields = ['cle', 'valeur', 'description']
        labels = {
            'cle': 'Clé de configuration',
            'valeur': 'Valeur',
            'description': 'Description',
        }
        widgets = {
            'valeur': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }

class ActionLogForm(forms.ModelForm):
    class Meta:
        model = ActionLog
        fields = ['utilisateur', 'action', 'details', 'entite', 'entite_id']
        labels = {
            'utilisateur': 'Utilisateur',
            'action': 'Action effectuée',
            'details': 'Détails',
            'entite': 'Entité concernée',
            'entite_id': 'ID de l’entité',
        }
        widgets = {
            'details': forms.Textarea(attrs={'rows': 2}),
        }

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['destinataire', 'message', 'type']
        labels = {
            'destinataire': 'Destinataire',
            'message': 'Message',
            'type': 'Type de notification',
        }
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
            'type': forms.Select(),
        }
