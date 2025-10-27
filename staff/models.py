from django.db import models
from django.utils import timezone
from accounts.models import User

class Employe(models.Model):
    """Informations détaillées des employés"""
    ETAT_CIVIL_CHOICES = [
        ('celibataire', 'Célibataire'),
        ('marie', 'Marié(e)'),
        ('divorce', 'Divorcé(e)'),
        ('veuf', 'Veuf/Veuve'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employe')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=100, blank=True)
    nationalite = models.CharField(max_length=50)
    etat_civil = models.CharField(max_length=20, choices=ETAT_CIVIL_CHOICES)
    
    adresse = models.TextField()
    ville = models.CharField(max_length=100)
    pays = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    
    poste = models.CharField(max_length=100)
    departement = models.CharField(max_length=100)
    date_embauche = models.DateField()
    salaire = models.DecimalField(max_digits=10, decimal_places=2)
    
    cv = models.FileField(upload_to='cv_employes/', blank=True, null=True)
    contrat = models.FileField(upload_to='contrats/', blank=True, null=True)
    photo = models.ImageField(upload_to='photos_employes/', blank=True, null=True)
    
    contact_urgence_nom = models.CharField(max_length=100, blank=True)
    contact_urgence_phone = models.CharField(max_length=20, blank=True)
    contact_urgence_relation = models.CharField(max_length=50, blank=True)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employes'
        verbose_name = 'Employé'
        verbose_name_plural = 'Employés'
    
    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.poste}"

class Planning(models.Model):
    """Planning de travail des employés"""
    PERIODE_CHOICES = [
        ('jour', 'Jour (06h-14h)'),
        ('soir', 'Soir (14h-22h)'),
        ('nuit', 'Nuit (22h-06h)'),
    ]
    
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='plannings')
    date = models.DateField()
    periode = models.CharField(max_length=10, choices=PERIODE_CHOICES)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    poste_assigne = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'plannings'
        unique_together = ['employe', 'date', 'periode']
        ordering = ['date', 'heure_debut']

class Pointage(models.Model):
    """Enregistrement des pointages"""
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='pointages')
    date = models.DateField()
    heure_arrivee = models.TimeField()
    heure_depart = models.TimeField(null=True, blank=True)
    retard_minutes = models.IntegerField(default=0)
    heures_travaillees = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'pointages'
        unique_together = ['employe', 'date']
        ordering = ['-date']

class Conge(models.Model):
    """Gestion des congés et absences"""
    TYPE_CHOICES = [
        ('conge_annuel', 'Congé annuel'),
        ('conge_maladie', 'Congé maladie'),
        ('conge_maternite', 'Congé maternité'),
        ('conge_sans_solde', 'Congé sans solde'),
        ('absence', 'Absence'),
    ]
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('refuse', 'Refusé'),
    ]
    
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='conges')
    type_conge = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date_debut = models.DateField()
    date_fin = models.DateField()
    nombre_jours = models.IntegerField()
    motif = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    approuve_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='conges_approuves')
    date_demande = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conges'
        ordering = ['-date_demande']

class Evaluation(models.Model):
    """Évaluations des employés"""
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='evaluations')
    date_evaluation = models.DateField()
    periode_evaluee = models.CharField(max_length=100)
    evaluateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    objectifs = models.TextField()
    realisations = models.TextField()
    points_forts = models.TextField(blank=True)
    points_amelioration = models.TextField(blank=True)
    note_globale = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    commentaires = models.TextField(blank=True)
    
    class Meta:
        db_table = 'evaluations'
        ordering = ['-date_evaluation']

class Incident(models.Model):
    """Incidents et sanctions"""
    TYPE_CHOICES = [
        ('retard', 'Retard'),
        ('absence', 'Absence injustifiée'),
        ('comportement', 'Problème de comportement'),
        ('performance', 'Performance insuffisante'),
        ('autre', 'Autre'),
    ]
    
    SANCTION_CHOICES = [
        ('avertissement', 'Avertissement verbal'),
        ('blame', 'Blâme écrit'),
        ('suspension', 'Suspension'),
        ('mise_pied', 'Mise à pied'),
    ]
    
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='incidents')
    date_incident = models.DateField()
    type_incident = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()
    sanction = models.CharField(max_length=20, choices=SANCTION_CHOICES, blank=True)
    date_sanction = models.DateField(null=True, blank=True)
    signale_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'incidents'
        ordering = ['-date_incident']