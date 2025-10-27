from django.db import models
from django.utils import timezone

class Client(models.Model):
    """Modèle pour les clients de l'hôtel"""
    CIVILITE_CHOICES = [
        ('M', 'Monsieur'),
        ('Mme', 'Madame'),
        ('Mlle', 'Mademoiselle'),
    ]
    
    civilite = models.CharField(max_length=5, choices=CIVILITE_CHOICES)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField(null=True, blank=True)
    nationalite = models.CharField(max_length=50, blank=True)
    adresse = models.TextField(blank=True)
    ville = models.CharField(max_length=100, blank=True)
    pays = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    
    type_piece = models.CharField(max_length=50, blank=True)
    numero_piece = models.CharField(max_length=50, blank=True)
    piece_identite = models.FileField(upload_to='pieces_identite/', blank=True, null=True)
    
    type_chambre_prefere = models.CharField(max_length=50, blank=True)
    preferences_speciales = models.TextField(blank=True)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'clients'
        ordering = ['-date_creation']
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
    
    def __str__(self):
        return f"{self.civilite} {self.nom} {self.prenom}"
    
    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

class HistoriqueClient(models.Model):
    """Historique des séjours et interactions clients"""
    TYPE_CHOICES = [
        ('sejour', 'Séjour'),
        ('incident', 'Incident'),
        ('reclamation', 'Réclamation'),
        ('compliment', 'Compliment'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='historiques')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    montant = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'historique_clients'
        ordering = ['-date']