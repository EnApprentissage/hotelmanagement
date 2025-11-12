from decimal import Decimal
from django.utils import timezone # CORRECT
# OU : from django.utils.timezone import now
from time import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from parametrage.reference_generator import ReferenceGenerator
from django.conf import settings


class Employe(models.Model):
    """Informations détaillées des employés"""
    ETAT_CIVIL_CHOICES = [
        ('celibataire', _('Célibataire')),
        ('marie', _('Marié(e)')),
        ('divorce', _('Divorcé(e)')),
        ('veuf', _('Veuf/Veuve')),
    ]

    # === RELATION & IDENTITÉ ===
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='employes',
        verbose_name=_("Créé par")
    )
    nom = models.CharField(_("Nom"), max_length=100)
    prenom = models.CharField(_("Prénom"), max_length=100)
    date_naissance = models.DateField(_("Date de naissance"), null=True, blank=True)
    lieu_naissance = models.CharField(_("Lieu de naissance"), max_length=100, blank=True)
    nationalite = models.CharField(_("Nationalité"), max_length=50, default="Marocaine")
    etat_civil = models.CharField(_("État civil"), max_length=20, choices=ETAT_CIVIL_CHOICES, default='celibataire')
    matricule = models.CharField(
        _("Matricule"),
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    # === CONTACT ===
    adresse = models.TextField(_("Adresse"))
    ville = models.CharField(_("Ville"), max_length=100)
    pays = models.CharField(_("Pays"), max_length=100, default="Maroc")
    phone = models.CharField(_("Téléphone"), max_length=20)
    email = models.EmailField(_("Email"))

    # === TRAVAIL ===
    poste = models.CharField(_("Poste"), max_length=100)
    departement = models.CharField(_("Département"), max_length=100)
    date_embauche = models.DateField(_("Date d'embauche"), null=True, blank=True)
    salaire = models.DecimalField(
        _("Salaire"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # === DOCUMENTS & MÉDIAS ===
    cv = models.FileField(upload_to='cv_employes/', blank=True, null=True, verbose_name=_("CV"))
    contrat = models.FileField(upload_to='contrats/', blank=True, null=True, verbose_name=_("Contrat"))
    photo = models.ImageField(
        upload_to='photos_employes/',
        blank=True,
        null=True,
        verbose_name=_("Photo")
    )

    # === POINTAGE PAR CARTE ===
    carte_id = models.CharField(
        _("ID Carte (RFID/NFC)"),
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text=_("Scannez la carte pour associer cet ID")
    )

    # === URGENCE ===
    contact_urgence_nom = models.CharField(_("Nom contact urgence"), max_length=100, blank=True)
    contact_urgence_phone = models.CharField(_("Téléphone urgence"), max_length=20, blank=True)
    contact_urgence_relation = models.CharField(_("Relation"), max_length=50, blank=True)

    # === AUDIT ===
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
    date_modification = models.DateTimeField(auto_now=True, verbose_name=_("Modifié le"))

    class Meta:
        db_table = 'employes'
        verbose_name = 'Employé'
        verbose_name_plural = 'Employés'
        ordering = ['-date_embauche', 'nom']

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.poste}"

    def get_full_name(self):
        return f"{self.prenom} {self.nom}"

    def get_photo_url(self):
        if self.photo:
            return self.photo.url
        return f"{settings.STATIC_URL}img/default-avatar.png"  # À configurer

    # === GÉNÉRATION AUTOMATIQUE DU MATRICULE ===
    def save(self, *args, **kwargs):
        if not self.matricule:
            self.matricule = ReferenceGenerator.generate_reference(
                model_class=Employe,
                field_name='matricule',
                prefix='EMP',
                nombre=4
            )
        super().save(*args, **kwargs)

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



from django.db import models
from django.utils import timezone  # CORRECT
# OU : from django.utils.timezone import now
from decimal import Decimal

class Pointage(models.Model):
    employe = models.ForeignKey(
        'Employe',
        on_delete=models.CASCADE,
        related_name='pointages',
        verbose_name="Employé"
    )
    date = models.DateField(
        _("Date"),
        default=timezone.now  # FONCTION, PAS APPELÉE ICI
        # Si tu veux la date sans heure : default=timezone.now.date
    )
    heure_arrivee = models.TimeField(_("Heure d'arrivée"))
    heure_depart = models.TimeField(_("Heure de départ"), null=True, blank=True)
    retard_minutes = models.IntegerField(_("Retard (min)"), default=0)
    heures_travaillees = models.DecimalField(
        _("Heures travaillées"),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    notes = models.TextField(_("Notes"), blank=True)

    class Meta:
        db_table = 'pointages'
        unique_together = ['employe', 'date']
        ordering = ['-date', '-heure_arrivee']
        verbose_name = 'Pointage'
        verbose_name_plural = 'Pointages'

    def __str__(self):
        return f"{self.employe} - {self.date}"

    def calculer_retard(self):
        heure_standard = timezone.datetime.strptime("08:00", "%H:%M").time()
        if self.heure_arrivee and self.heure_arrivee > heure_standard:
            delta = timezone.datetime.combine(timezone.now().date(), self.heure_arrivee) - \
                    timezone.datetime.combine(timezone.now().date(), heure_standard)
            self.retard_minutes = delta.seconds // 60
        else:
            self.retard_minutes = 0
        self.save(update_fields=['retard_minutes'])

    def calculer_heures_travaillees(self):
        if self.heure_arrivee and self.heure_depart:
            delta = timezone.datetime.combine(timezone.now().date(), self.heure_depart) - \
                    timezone.datetime.combine(timezone.now().date(), self.heure_arrivee)
            heures = Decimal(delta.seconds) / 3600
            self.heures_travaillees = round(heures, 2)
        else:
            self.heures_travaillees = None
        self.save(update_fields=['heures_travaillees'])

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
    approuve_par = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name='conges_approuves')
    date_demande = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conges'
        ordering = ['-date_demande']

class Evaluation(models.Model):
    """Évaluations des employés"""
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='evaluations')
    date_evaluation = models.DateField()
    periode_evaluee = models.CharField(max_length=100)
    evaluateur = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    
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
    signale_par = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'incidents'
        ordering = ['-date_incident']
