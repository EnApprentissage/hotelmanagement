# reports/models.py
from django.db import models
from django.utils import timezone
from datetime import date


class ReportQuerySet(models.QuerySet):
    def period(self, start_date=None, end_date=None):
        if start_date:
            self = self.filter(date__gte=start_date)
        if end_date:
            self = self.filter(date__lte=end_date)
        return self


class DailyReport(models.Model):
    """
    Rapport journalier agrégé (calculé chaque nuit ou via tâche Celery)
    """
    date = models.DateField(unique=True, default=timezone.now)
    
    # Occupation
    chambres_total = models.PositiveIntegerField()
    chambres_occupees = models.PositiveIntegerField()
    taux_occupation = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # %

    # Réservations
    reservations_nouvelles = models.PositiveIntegerField(default=0)
    reservations_annulees = models.PositiveIntegerField(default=0)
    no_show = models.PositiveIntegerField(default=0)

    # Revenus
    ca_hebergement = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ca_restauration = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ca_bar = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ca_autres = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    ca_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # ADR & RevPAR
    adr = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    revpar = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Clients
    clients_nouveaux = models.PositiveIntegerField(default=0)
    clients_recurrents = models.PositiveIntegerField(default=0)

    # Création
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ReportQuerySet.as_manager()

    class Meta:
        verbose_name = "Rapport Journalier"
        verbose_name_plural = "Rapports Journaliers"
        ordering = ['-date']

    def __str__(self):
        return f"Rapport du {self.date}"

    def save(self, *args, **kwargs):
        # Calcul auto du taux d'occupation
        if self.chambres_total > 0:
            self.taux_occupation = round(
                (self.chambres_occupees / self.chambres_total) * 100, 2
            )
        # CA total
        self.ca_total = (
            self.ca_hebergement + self.ca_restauration +
            self.ca_bar + self.ca_autres
        )
        super().save(*args, **kwargs)