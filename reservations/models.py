from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from clients.models import Client
from chambres.models import Chambre
from accounts.models import User

class Reservation(models.Model):
    """Réservations de chambres"""
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('en_cours', 'En cours (check-in effectué)'),
        ('terminee', 'Terminée (check-out effectué)'),
        ('annulee', 'Annulée'),
        ('no_show', 'No-show (Absent)'),
    ]
    
    TYPE_CHOICES = [
        ('directe', 'Réservation directe'),
        ('en_ligne', 'Réservation en ligne'),
        ('agence', 'Agence de voyage'),
        ('telephone', 'Téléphone'),
    ]
    
    numero_reservation = models.CharField(max_length=20, unique=True, editable=False)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='reservations')
    chambre = models.ForeignKey(Chambre, on_delete=models.PROTECT, related_name='reservations')
    
    date_arrivee = models.DateField()
    date_depart = models.DateField()
    date_checkin = models.DateTimeField(null=True, blank=True)
    date_checkout = models.DateTimeField(null=True, blank=True)
    
    nombre_adultes = models.IntegerField(default=1)
    nombre_enfants = models.IntegerField(default=0)
    
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    type_reservation = models.CharField(max_length=20, choices=TYPE_CHOICES, default='directe')
    
    prix_par_nuit = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    acompte = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    demandes_speciales = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reservations_creees')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reservations'
        ordering = ['-date_creation']
        verbose_name = 'Réservation'
        verbose_name_plural = 'Réservations'
    
    def __str__(self):
        return f"Réservation {self.numero_reservation} - {self.client.nom_complet}"
    
    def save(self, *args, **kwargs):
        if not self.numero_reservation:
            self.numero_reservation = f"RES{timezone.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)
    
    @property
    def nombre_nuits(self):
        return (self.date_depart - self.date_arrivee).days
    
    def perform_check_in(self):
        """Gère le check-in"""
        if self.statut == 'confirmee':
            self.statut = 'en_cours'
            self.date_checkin = timezone.now()
            self.chambre.statut = 'occupee'
            self.chambre.save()
            self.save()
    
    def perform_check_out(self):
        """Gère le check-out"""
        if self.statut == 'en_cours':
            self.statut = 'terminee'
            self.date_checkout = timezone.now()
            self.chambre.statut = 'sale'
            self.chambre.save()
            self.save()

@receiver(post_save, sender=Reservation)
def update_chambre_status(sender, instance, **kwargs):
    """Met à jour le statut de la chambre en fonction de la réservation"""
    if instance.statut == 'confirmee':
        instance.chambre.statut = 'reservee'
        instance.chambre.save()
    elif instance.statut in ['annulee', 'no_show', 'terminee']:
        instance.chambre.statut = 'disponible' if instance.chambre.statut != 'en_maintenance' else instance.chambre.statut
        instance.chambre.save()