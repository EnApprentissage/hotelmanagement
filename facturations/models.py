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
    reservation = models.ForeignKey(
        Reservation, on_delete=models.SET_NULL, null=True, blank=True, related_name='factures'
    )
    commande_resto = models.ForeignKey(
        Commande, on_delete=models.SET_NULL, null=True, blank=True, related_name='factures_resto'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'factures'
        ordering = ['-date_creation']
        verbose_name = "Facture"
        verbose_name_plural = "Factures"

    def save(self, *args, **kwargs):
        """Génération automatique du numéro de facture"""
        if not self.numero_facture:
            last_facture = Facture.objects.order_by('-id').first()
            next_id = (last_facture.id + 1) if last_facture else 1
            self.numero_facture = f"FAC{timezone.now().strftime('%Y%m%d')}-{next_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero_facture} - {self.client.nom_complet}"

    @property
    def montant_paye(self):
        """Somme totale des paiements liés à la facture"""
        return sum(p.montant for p in self.paiements.all())

    @property
    def reste_a_payer(self):
        """Montant restant dû"""
        return self.montant_total - self.montant_paye

    def marquer_comme_payee(self):
        """Met à jour le statut si le paiement est complet"""
        if self.reste_a_payer <= 0:
            self.statut = 'payee'
            self.save()


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
    effectue_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'paiements'
        ordering = ['-date_paiement']
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"

    def __str__(self):
        return f"{self.facture.numero_facture} - {self.montant} {self.get_mode_paiement_display()}"

    def save(self, *args, **kwargs):
        """Met à jour automatiquement la facture après paiement"""
        super().save(*args, **kwargs)
        self.facture.marquer_comme_payee()
