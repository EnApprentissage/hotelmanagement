from django import forms
from core.models import SystemConfig, Notification

class SystemConfigForm(forms.ModelForm):
    """Formulaire pour les configurations du système"""
    class Meta:
        model = SystemConfig
        fields = ['cle', 'valeur', 'description']
        widgets = {
            'valeur': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_cle(self):
        """Valider l'unicité de la clé"""
        cle = self.cleaned_data.get('cle')
        if SystemConfig.objects.filter(cle=cle).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise forms.ValidationError("Cette clé existe déjà.")
        return cle

class NotificationForm(forms.ModelForm):
    """Formulaire pour les notifications"""
    class Meta:
        model = Notification
        fields = ['destinataire', 'message', 'type', 'lu']
        widgets = {
            'destinataire': forms.Select(),
            'type': forms.Select(choices=Notification.TYPE_CHOICES),
            'message': forms.Textarea(attrs={'rows': 4}),
            'lu': forms.CheckboxInput(),
        }