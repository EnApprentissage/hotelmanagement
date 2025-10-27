from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from accounts.models import User  # Importation pour les relations avec User

class TypeChambre(models.Model):
    """Types de chambres disponibles"""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    capacite_adultes = models.IntegerField(default=2)
    capacite_enfants = models.IntegerField(default=0)
    superficie = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    prix_base = models.DecimalField(max_digits=10, decimal_places=2)
    equipements = models.TextField(blank=True, help_text="Liste des équipements séparés par des virgules")
    image = models.ImageField(upload_to='types_chambres/', blank=True, null=True)
    
    class Meta:
        db_table = 'types_chambres'
        verbose_name = 'Type de chambre'
        verbose_name_plural = 'Types de chambres'
    
    def __str__(self):
        return self.nom

class Chambre(models.Model):
    """Chambres de l'hôtel"""
    STATUT_CHOICES = [
        ('disponible', 'Disponible'),
        ('reservee', 'Réservée'),
        ('occupee', 'Occupée'),
        ('sale', 'Sale (à nettoyer)'),
        ('en_nettoyage', 'En cours de nettoyage'),
        ('propre', 'Propre'),
        ('en_maintenance', 'En maintenance'),
        ('hors_service', 'Hors service'),
    ]
    
    numero = models.CharField(max_length=10, unique=True)
    type_chambre = models.ForeignKey(TypeChambre, on_delete=models.PROTECT, related_name='chambres')
    etage = models.IntegerField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='disponible')
    description = models.TextField(blank=True)
    notes_internes = models.TextField(blank=True)
    date_derniere_maintenance = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'chambres'
        ordering = ['numero']
        verbose_name = 'Chambre'
        verbose_name_plural = 'Chambres'
    
    def __str__(self):
        return f"Chambre {self.numero} - {self.type_chambre.nom}"

class MaintenanceChambre(models.Model):
    """Suivi des maintenances et réparations"""
    STATUT_CHOICES = [
        ('signale', 'Signalé'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
    ]
    
    PRIORITE_CHOICES = [
        ('basse', 'Basse'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('urgente', 'Urgente'),
    ]
    
    chambre = models.ForeignKey(Chambre, on_delete=models.CASCADE, related_name='maintenances')
    date_signalement = models.DateTimeField(auto_now_add=True)
    signale_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='maintenances_signalees')
    probleme = models.TextField()
    priorite = models.CharField(max_length=10, choices=PRIORITE_CHOICES, default='normale')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='signale')
    date_debut = models.DateTimeField(null=True, blank=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    technicien = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenances_effectuees')
    cout = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'maintenances_chambres'
        ordering = ['-date_signalement']

@receiver(post_save, sender=MaintenanceChambre)
def update_chambre_maintenance(sender, instance, **kwargs):
    """Met à jour le statut de la chambre en fonction de la maintenance"""
    if instance.statut in ['signale', 'en_cours']:
        instance.chambre.statut = 'en_maintenance'
    elif instance.statut in ['termine', 'annule']:
        instance.chambre.statut = 'propre' if instance.chambre.statut != 'occupee' else instance.chambre.statut
    instance.chambre.date_derniere_maintenance = instance.date_fin or timezone.now()
    instance.chambre.save()