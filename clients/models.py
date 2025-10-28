from django.db import models
from django.utils import timezone
from datetime import date


class Client(models.Model):
    """Informations détaillées sur les clients de l'hôtel"""

    CIVILITE_CHOICES = [
        ('M', 'Monsieur'),
        ('Mme', 'Madame'),
        ('Mlle', 'Mademoiselle'),
    ]

    civilite = models.CharField(max_length=5, choices=CIVILITE_CHOICES, verbose_name="Civilité")
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    date_naissance = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    nationalite = models.CharField(max_length=50, blank=True, verbose_name="Nationalité")
    adresse = models.TextField(blank=True, verbose_name="Adresse complète")
    ville = models.CharField(max_length=100, blank=True, verbose_name="Ville")
    pays = models.CharField(max_length=100, blank=True, verbose_name="Pays")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Adresse email")

    type_piece = models.CharField(max_length=50, blank=True, verbose_name="Type de pièce d’identité")
    numero_piece = models.CharField(max_length=50, blank=True, verbose_name="Numéro de pièce d’identité")
    piece_identite = models.FileField(
        upload_to='pieces_identite/', blank=True, null=True, verbose_name="Pièce d’identité (fichier)"
    )

    type_chambre_prefere = models.CharField(max_length=50, blank=True, verbose_name="Type de chambre préféré")
    preferences_speciales = models.TextField(blank=True, verbose_name="Préférences spéciales")

    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date d’enregistrement")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    notes = models.TextField(blank=True, verbose_name="Notes internes")

    class Meta:
        db_table = 'clients'
        ordering = ['-date_creation']
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        nom_affiche = f"{self.nom.upper()} {self.prenom.title()}" if self.nom and self.prenom else "Client inconnu"
        return f"{self.get_civilite_display()} {nom_affiche}"

    @property
    def nom_complet(self):
        """Retourne le nom complet (utile pour les rapports et factures)"""
        return f"{self.prenom.title()} {self.nom.upper()}"

    @property
    def age(self):
        """Calcule l’âge du client s’il a une date de naissance"""
        if self.date_naissance:
            today = date.today()
            return today.year - self.date_naissance.year - (
                (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day)
            )
        return None

    def dernier_sejour(self):
        """Retourne le dernier séjour enregistré dans l’historique"""
        return self.historiques.filter(type='sejour').order_by('-date').first()


class HistoriqueClient(models.Model):
    """Historique des séjours, incidents ou interactions liés à un client"""

    TYPE_CHOICES = [
        ('sejour', 'Séjour'),
        ('incident', 'Incident'),
        ('reclamation', 'Réclamation'),
        ('compliment', 'Compliment'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='historiques', verbose_name="Client associé")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type d’interaction")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Date de l’événement")
    description = models.TextField(verbose_name="Description détaillée")
    montant = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Montant lié (optionnel)")

    class Meta:
        db_table = 'historique_clients'
        ordering = ['-date']
        verbose_name = 'Historique client'
        verbose_name_plural = 'Historiques clients'

    def __str__(self):
        return f"{self.client.nom_complet} - {self.get_type_display()} ({self.date.strftime('%d/%m/%Y')})"
