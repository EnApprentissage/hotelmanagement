from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class User(AbstractUser):
    """Modèle utilisateur personnalisé"""
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('manager', 'Manager/Directeur'),
        ('receptionniste', 'Réceptionniste'),
        ('resto_staff', 'Personnel Resto'),
        ('bar_staff', 'Personnel Bar'),
        ('comptable', 'Comptable/Caissier'),
        ('gouvernante', 'Gouvernante'),
        ('menage', 'Femme de chambre'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_active_employee = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
    
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"

@receiver(post_save, sender=User)
def create_employe(sender, instance, created, **kwargs):
    """Crée un Employe pour les rôles liés au personnel si nécessaire"""
    if created and instance.role in ['receptionniste', 'resto_staff', 'bar_staff', 'comptable', 'gouvernante', 'menage']:
        # ✅ Import différé pour éviter l'import circulaire
        from staff.models import Employe  
        Employe.objects.get_or_create(user=instance, defaults={
            'nom': instance.last_name,
            'prenom': instance.first_name,
            'email': instance.email,
            'phone': instance.phone,
        })
