from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from accounts.models import User
from chambres.models import TypeChambre, Chambre
from core.models import Notification, ActionLog

class CategorieInventaire(models.Model):
    """Catégories de produits d'inventaire"""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'categories_inventaire'
        verbose_name = 'Catégorie inventaire'
        verbose_name_plural = 'Catégories inventaire'
    
    def __str__(self):
        return self.nom

class Produit(models.Model):
    """Produits en stock"""
    code = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    categorie = models.ForeignKey(CategorieInventaire, on_delete=models.PROTECT, related_name='produits')
    
    stock_actuel = models.IntegerField(default=0)
    stock_minimum = models.IntegerField(default=10)
    stock_maximum = models.IntegerField(default=100)
    
    unite_mesure = models.CharField(max_length=20, default='unité')
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    emplacement = models.CharField(max_length=100, blank=True)
    
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'produits'
        ordering = ['nom']
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
    
    def __str__(self):
        return f"{self.code} - {self.nom}"
    
    @property
    def est_en_rupture(self):
        return self.stock_actuel == 0
    
    @property
    def est_en_alerte(self):
        return self.stock_actuel <= self.stock_minimum

@receiver(post_save, sender=Produit)
def check_stock_alert(sender, instance, **kwargs):
    """Crée une notification si le stock est bas ou en rupture"""
    if instance.est_en_rupture or instance.est_en_alerte:
        Notification.objects.create(
            destinataire=None,  # À définir selon le rôle (ex. gouvernante)
            message=f"Stock {'en rupture' if instance.est_en_rupture else 'bas'} pour {instance.nom} ({instance.stock_actuel} unités)",
            type='stock_alert'
        )

class MouvementStock(models.Model):
    """Mouvements d'entrée/sortie de stock"""
    TYPE_CHOICES = [
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
        ('ajustement', 'Ajustement inventaire'),
        ('perte', 'Perte/Casse'),
    ]
    
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT, related_name='mouvements')
    type_mouvement = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantite = models.IntegerField()
    date_mouvement = models.DateTimeField(auto_now_add=True)
    
    motif = models.CharField(max_length=200, blank=True)
    bon_livraison = models.CharField(max_length=100, blank=True)
    effectue_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'mouvements_stock'
        ordering = ['-date_mouvement']

@receiver(post_save, sender=MouvementStock)
def update_stock(sender, instance, **kwargs):
    """Met à jour le stock actuel du produit"""
    if instance.type_mouvement == 'entree':
        instance.produit.stock_actuel += instance.quantite
    elif instance.type_mouvement in ['sortie', 'perte']:
        instance.produit.stock_actuel -= instance.quantite
    instance.produit.save()

class DemandeReapprovisionnement(models.Model):
    """Demandes de réapprovisionnement"""
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuvee', 'Approuvée'),
        ('commandee', 'Commandée'),
        ('recue', 'Reçue'),
        ('annulee', 'Annulée'),
    ]
    
    numero_demande = models.CharField(max_length=20, unique=True, editable=False)
    date_demande = models.DateTimeField(auto_now_add=True)
    demande_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='demandes_reappro')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    
    approuve_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='demandes_approuvees')
    date_approbation = models.DateTimeField(null=True, blank=True)
    
    date_reception = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'demandes_reapprovisionnement'
        ordering = ['-date_demande']
    
    def save(self, *args, **kwargs):
        if not self.numero_demande:
            self.numero_demande = f"DEM{timezone.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)

class LigneDemandeReapprovisionnement(models.Model):
    """Lignes de demande de réapprovisionnement"""
    demande = models.ForeignKey(DemandeReapprovisionnement, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    quantite_demandee = models.IntegerField()
    quantite_recue = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'lignes_demandes_reappro'

class InventairePhysique(models.Model):
    """Inventaires physiques"""
    STATUT_CHOICES = [
        ('en_cours', 'En cours'),
        ('valide', 'Validé'),
        ('annule', 'Annulé'),
    ]
    
    numero_inventaire = models.CharField(max_length=20, unique=True, editable=False)
    date_inventaire = models.DateField()
    effectue_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_cours')
    date_validation = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'inventaires_physiques'
        ordering = ['-date_inventaire']
    
    def save(self, *args, **kwargs):
        if not self.numero_inventaire:
            self.numero_inventaire = f"INV{timezone.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)

class LigneInventairePhysique(models.Model):
    """Lignes d'inventaire physique"""
    inventaire = models.ForeignKey(InventairePhysique, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    quantite_theorique = models.IntegerField()
    quantite_physique = models.IntegerField(null=True, blank=True)
    ecart = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'lignes_inventaires_physiques'
        unique_together = ['inventaire', 'produit']

class DotationChambre(models.Model):
    """Dotations standard par type de chambre"""
    type_chambre = models.ForeignKey(TypeChambre, on_delete=models.CASCADE, related_name='dotations')
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    quantite_standard = models.IntegerField()
    frequence_renouvellement = models.CharField(max_length=50, help_text="ex: Quotidien, Hebdomadaire")
    
    class Meta:
        db_table = 'dotations_chambres'
        unique_together = ['type_chambre', 'produit']

@receiver(post_save, sender=DotationChambre)
def update_stock_on_dotation(sender, instance, **kwargs):
    """Met à jour le stock lorsqu'une dotation est utilisée"""
    produit = instance.produit
    produit.stock_actuel -= instance.quantite_standard
    produit.save()
    ActionLog.objects.create(
        utilisateur=None,  # À définir via middleware
        action='dotation_used',
        details=f"Used {instance.quantite_standard} of {produit.nom} for {instance.type_chambre}",
        entite='DotationChambre',
        entite_id=instance.id
    )

class Signalement(models.Model):
    """Signalements du personnel"""
    TYPE_CHOICES = [
        ('manque_produit', 'Manque de produit'),
        ('materiel_casse', 'Matériel cassé'),
        ('probleme_chambre', 'Problème chambre'),
        ('autre', 'Autre'),
    ]
    
    STATUT_CHOICES = [
        ('ouvert', 'Ouvert'),
        ('en_cours', 'En cours'),
        ('resolu', 'Résolu'),
    ]
    
    type_signalement = models.CharField(max_length=20, choices=TYPE_CHOICES)
    chambre = models.ForeignKey(Chambre, on_delete=models.SET_NULL, null=True, blank=True, related_name='signalements')
    produit = models.ForeignKey(Produit, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ouvert')
    
    signale_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='signalements_faits')
    date_signalement = models.DateTimeField(auto_now_add=True)
    
    traite_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='signalements_traites')
    date_traitement = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'signalements'
        ordering = ['-date_signalement']