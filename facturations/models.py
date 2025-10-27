from django.db import models
from django.utils import timezone
from clients.models import Client
from reservations.models import Reservation
from resto_bar.models import Commande
from accounts.models import User

class Facture(models.Model):
    """Factures pour les clients"""
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
    ]
    
    numero_facture = models.CharField(max_length=20, unique=True, editable=False)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='factures')
    reservation = models.ForeignKey(Reservation, on_delete=models.SET_NULL, null=True, blank=True, related_name='factures')
    commande_resto = models.ForeignKey(Commande, on_delete=models.SET_NULL, null=True, blank=True, related_name='factures_resto')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'factures'
        ordering = ['-date_creation']
    
    def save(self, *args, **kwargs):
        if not self.numero_facture:
            self.numero_facture = f"FAC{timezone.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Facture {self.numero_facture} - {self.client.nom_complet}"

class Paiement(models.Model):
    """Paiements des factures"""
    MODE_CHOICES = [
        ('especes', 'Espèces'),
        ('carte', 'Carte bancaire'),
        ('mobile', 'Paiement mobile'),
        ('cheque', 'Chèque'),
    ]
    
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='paiements')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    mode_paiement = models.CharField(max_length=20, choices=MODE_CHOICES)
    date_paiement = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=50, blank=True)
    effectue_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'paiements'
        ordering = ['-date_paiement']