from django.db import models
from django.utils import timezone
from accounts.models import User

class SystemConfig(models.Model):
    """Configurations globales du système"""
    cle = models.CharField(max_length=100, unique=True)
    valeur = models.TextField()
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'system_configs'
        verbose_name = 'Configuration'
        verbose_name_plural = 'Configurations'
    
    def __str__(self):
        return self.cle

class ActionLog(models.Model):
    """Journal des actions du système"""
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    entite = models.CharField(max_length=50, blank=True)
    entite_id = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'action_logs'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.action} by {self.utilisateur} at {self.date}"

class Notification(models.Model):
    """Notifications du système"""
    TYPE_CHOICES = [
        ('stock_alert', 'Alerte Stock'),
        ('maintenance', 'Maintenance'),
        ('reservation', 'Réservation'),
        ('signalement', 'Signalement'),
    ]
    
    destinataire = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    message = models.TextField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-date']
    
    def __str__(self):
        return f"Notification {self.get_type_display()} - {self.message[:50]}"