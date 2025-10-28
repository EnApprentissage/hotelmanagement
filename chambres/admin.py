# chambres/admin.py
from django.contrib import admin
from .models import TypeChambre


@admin.register(TypeChambre)
class TypeChambreAdmin(admin.ModelAdmin):
    """
    Admin simplifié et optimisé pour gérer les types de chambres
    même si l'hôtel est en construction (pas d'images nécessaires)
    """
    # Affichage dans la liste
    list_display = ('nom', 'prix_base', 'capacite_adultes', 'capacite_enfants', 'superficie')
    list_filter = ('capacite_adultes', 'capacite_enfants')
    search_fields = ('nom', 'description', 'equipements')
    ordering = ('prix_base',)

    # Organisation des champs dans le formulaire
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'description')
        }),
        ('Capacité & Prix', {
            'fields': ('capacite_adultes', 'capacite_enfants', 'superficie', 'prix_base')
        }),
        ('Équipements', {
            'fields': ('equipements',),
            'description': 'Séparez par des virgules : WiFi, TV, Climatisation...'
        }),
    )

    # Ajout rapide : permet de créer/modifier directement depuis la liste (optionnel)
    list_editable = ('prix_base', 'capacite_adultes', 'capacite_enfants')
