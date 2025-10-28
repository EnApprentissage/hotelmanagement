from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from accounts.models import User


class TypeChambre(models.Model):
    """Types de chambres disponibles dans l’hôtel"""
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom du type de chambre")
    description = models.TextField(blank=True, verbose_name="Description")
    capacite_adultes = models.IntegerField(default=2, verbose_name="Capacité adultes")
    capacite_enfants = models.IntegerField(default=0, verbose_name="Capacité enfants")
    superficie = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Superficie (m²)")
    prix_base = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix de base (par nuit)")
    equipements = models.TextField(blank=True, help_text="Liste des équipements séparés par des virgules")
    image = models.ImageField(upload_to='types_chambres/', blank=True, null=True, verbose_name="Image")

    class Meta:
        db_table = 'types_chambres'
        verbose_name = 'Type de chambre'
        verbose_name_plural = 'Types de chambres'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Chambre(models.Model):
    """Chambres physiques dans l’hôtel"""
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

    numero = models.CharField(max_length=10, unique=True, verbose_name="Numéro de chambre")
    type_chambre = models.ForeignKey(TypeChambre, on_delete=models.PROTECT, related_name='chambres', verbose_name="Type de chambre")
    etage = models.IntegerField(verbose_name="Étage")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='disponible', verbose_name="Statut")
    description = models.TextField(blank=True, verbose_name="Description")
    notes_internes = models.TextField(blank=True, verbose_name="Notes internes")
    date_derniere_maintenance = models.DateField(null=True, blank=True, verbose_name="Dernière maintenance")

    class Meta:
        db_table = 'chambres'
        ordering = ['numero']
        verbose_name = 'Chambre'
        verbose_name_plural = 'Chambres'

    def __str__(self):
        return f"Chambre {self.numero} ({self.type_chambre.nom})"

    def get_latest_maintenance(self):
        """Retourne la dernière maintenance effectuée"""
        return self.maintenances.order_by('-date_signalement').first()


class MaintenanceChambre(models.Model):
    """Gestion des maintenances et réparations de chambres"""
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

    chambre = models.ForeignKey(Chambre, on_delete=models.CASCADE, related_name='maintenances', verbose_name="Chambre concernée")
    date_signalement = models.DateTimeField(auto_now_add=True, verbose_name="Date de signalement")
    signale_par = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='maintenances_signalees', verbose_name="Signalé par"
    )
    probleme = models.TextField(verbose_name="Description du problème")
    priorite = models.CharField(max_length=10, choices=PRIORITE_CHOICES, default='normale', verbose_name="Priorité")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='signale', verbose_name="Statut")
    date_debut = models.DateTimeField(null=True, blank=True, verbose_name="Début de maintenance")
    date_fin = models.DateTimeField(null=True, blank=True, verbose_name="Fin de maintenance")
    technicien = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenances_effectuees', verbose_name="Technicien"
    )
    cout = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Coût total")
    notes = models.TextField(blank=True, verbose_name="Notes supplémentaires")

    class Meta:
        db_table = 'maintenances_chambres'
        ordering = ['-date_signalement']
        verbose_name = 'Maintenance'
        verbose_name_plural = 'Maintenances'

    def __str__(self):
        return f"Maintenance #{self.id} - {self.chambre.numero} ({self.get_statut_display()})"


@receiver(post_save, sender=MaintenanceChambre)
def update_chambre_maintenance(sender, instance, **kwargs):
    """Met à jour automatiquement le statut de la chambre selon la maintenance."""
    chambre = instance.chambre

    # Mettre à jour le statut selon la maintenance
    if instance.statut in ['signale', 'en_cours']:
        new_status = 'en_maintenance'
    elif instance.statut in ['termine', 'annule']:
        # Si la chambre n'est pas occupée, elle redevient propre
        new_status = 'propre' if chambre.statut != 'occupee' else chambre.statut
    else:
        new_status = chambre.statut

    # Appliquer les modifications seulement si nécessaire
    if chambre.statut != new_status or not chambre.date_derniere_maintenance:
        chambre.statut = new_status
        chambre.date_derniere_maintenance = instance.date_fin or timezone.now()
        chambre.save(update_fields=['statut', 'date_derniere_maintenance'])
