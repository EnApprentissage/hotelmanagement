from django.db import models
from django.utils import timezone
from clients.models import Client
from accounts.models import User

class CategorieMenu(models.Model):
    """Catégories de menu"""
    TYPE_CHOICES = [
        ('resto', 'Restaurant'),
        ('bar', 'Bar'),
    ]
    
    nom = models.CharField(max_length=100)
    type_service = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    ordre_affichage = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'categories_menu'
        ordering = ['type_service', 'ordre_affichage']
        unique_together = ['nom', 'type_service']
    
    def __str__(self):
        return f"{self.nom} ({self.get_type_service_display()})"

class ProduitMenu(models.Model):
    """Produits du menu resto/bar"""
    TYPE_CHOICES = [
        ('resto', 'Restaurant'),
        ('bar', 'Bar'),
    ]
    
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    categorie = models.ForeignKey(CategorieMenu, on_delete=models.PROTECT, related_name='produits')
    stock_actuel = models.IntegerField(default=0)
    type_service = models.CharField(max_length=10, choices=TYPE_CHOICES)
    image = models.ImageField(upload_to='produits_menu/', blank=True, null=True)
    
    class Meta:
        db_table = 'produits_menu'
        ordering = ['nom']
    
    def __str__(self):
        return self.nom

class Table(models.Model):
    """Tables du restaurant/bar"""
    STATUT_CHOICES = [
        ('libre', 'Libre'),
        ('occupee', 'Occupée'),
        ('reservee', 'Réservée'),
    ]
    
    numero = models.CharField(max_length=10, unique=True)
    type_service = models.CharField(max_length=10, choices=[('resto', 'Restaurant'), ('bar', 'Bar')])
    capacite = models.IntegerField(default=4)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='libre')
    
    class Meta:
        db_table = 'tables'
        ordering = ['numero']
    
    def __str__(self):
        return f"Table {self.numero} ({self.get_type_service_display()})"

class Commande(models.Model):
    """Commandes resto/bar"""
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('servie', 'Servie'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
    ]
    
    numero_commande = models.CharField(max_length=20, unique=True, editable=False)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, related_name='commandes')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='commandes')
    produits = models.ManyToManyField(ProduitMenu, through='CommandeItem')
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    type_service = models.CharField(max_length=10, choices=[('resto', 'Restaurant'), ('bar', 'Bar')])
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    serveur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='commandes_servies')
    
    class Meta:
        db_table = 'commandes'
        ordering = ['-date_commande']
    
    def save(self, *args, **kwargs):
        if not self.numero_commande:
            self.numero_commande = f"CMD{timezone.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Commande {self.numero_commande} - {self.get_type_service_display()}"

class CommandeItem(models.Model):
    """Items d'une commande"""
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='items')
    produit = models.ForeignKey(ProduitMenu, on_delete=models.PROTECT)
    quantite = models.IntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'commande_items'