from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé basé sur AbstractUser.
    Ajoute des rôles spécifiques et des informations supplémentaires.
    """

    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('manager', 'Manager / Directeur'),
        ('receptionniste', 'Réceptionniste'),
        ('resto_staff', 'Personnel Restauration'),
        ('bar_staff', 'Personnel Bar'),
        ('comptable', 'Comptable / Caissier'),
        ('gouvernante', 'Gouvernante'),
        ('menage', 'Femme de chambre'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='receptionniste')
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Photo de profil")
    is_active_employee = models.BooleanField(default=True, verbose_name="Employé actif")

    class Meta:
        db_table = 'users'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def full_name(self):
        """Retourne le nom complet de l'utilisateur."""
        return f"{self.first_name} {self.last_name}".strip()

    def is_staff_member(self):
        """Vérifie si l'utilisateur fait partie du personnel."""
        return self.role in [
            'receptionniste',
            'resto_staff',
            'bar_staff',
            'comptable',
            'gouvernante',
            'menage',
        ]


# Import du modèle Employe ici pour éviter les problèmes d'import circulaire
from staff.models import Employe


@receiver(post_save, sender=User)
def create_employe(sender, instance, created, **kwargs):
    """
    Crée automatiquement un Employé lorsqu'un utilisateur du personnel est ajouté.
    Évite la duplication si l'employé existe déjà.
    """
    if created and instance.is_staff_member():
        Employe.objects.get_or_create(
            user=instance,
            defaults={
                'nom': instance.last_name or '',
                'prenom': instance.first_name or '',
                'email': instance.email or '',
                'phone': instance.phone or '',
            }
        )
