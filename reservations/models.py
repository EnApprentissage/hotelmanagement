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

    numero_reservation = models.CharField(max_length=25, unique=True, editable=False)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='reservations')
    chambre = models.ForeignKey(Chambre, on_delete=models.PROTECT, related_name='reservations')

    date_arrivee = models.DateField()
    date_depart = models.DateField()
    date_checkin = models.DateTimeField(null=True, blank=True)
    date_checkout = models.DateTimeField(null=True, blank=True)

    nombre_adultes = models.PositiveIntegerField(default=1)
    nombre_enfants = models.PositiveIntegerField(default=0)

    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    type_reservation = models.CharField(max_length=20, choices=TYPE_CHOICES, default='directe')

    prix_par_nuit = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    acompte = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    demandes_speciales = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservations_creees'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reservations'
        ordering = ['-date_creation']
        verbose_name = 'Réservation'
        verbose_name_plural = 'Réservations'

    def __str__(self):
        return f"{self.numero_reservation} - {self.client.nom_complet}"

    def save(self, *args, **kwargs):
        """Génère un numéro unique au moment de la création"""
        if not self.numero_reservation:
            prefix = timezone.now().strftime("RES%Y%m%d")
            last_resa = Reservation.objects.filter(numero_reservation__startswith=prefix).order_by('id').last()
            next_id = (last_resa.id + 1) if last_resa else 1
            self.numero_reservation = f"{prefix}-{next_id:04d}"
        super().save(*args, **kwargs)

    @property
    def nombre_nuits(self):
        """Calcule automatiquement le nombre de nuits"""
        return max((self.date_depart - self.date_arrivee).days, 1)

    def perform_check_in(self):
        """Effectue le check-in"""
        if self.statut == 'confirmee':
            self.statut = 'en_cours'
            self.date_checkin = timezone.now()
            self.chambre.statut = 'occupee'
            self.chambre.save()
            self.save()

    def perform_check_out(self):
        """Effectue le check-out"""
        if self.statut == 'en_cours':
            self.statut = 'terminee'
            self.date_checkout = timezone.now()
            self.chambre.statut = 'sale'
            self.chambre.save()
            self.save()

    @property
    def montant_restant(self):
        """Renvoie le montant restant à payer"""
        return max(self.total - self.acompte, 0)


@receiver(post_save, sender=Reservation)
def update_chambre_status(sender, instance, created, **kwargs):
    """Met à jour automatiquement le statut de la chambre en fonction de la réservation"""
    chambre = instance.chambre

    if instance.statut == 'confirmee':
        chambre.statut = 'reservee'
    elif instance.statut == 'en_cours':
        chambre.statut = 'occupee'
    elif instance.statut in ['terminee', 'annulee', 'no_show']:
        # Si la chambre n'est pas en maintenance, on la libère
        if chambre.statut != 'en_maintenance':
            chambre.statut = 'disponible'

    chambre.save()
