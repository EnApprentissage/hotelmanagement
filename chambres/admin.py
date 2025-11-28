# chambres/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import TypeChambre, Chambre, MaintenanceChambre


@admin.register(TypeChambre)
class TypeChambreAdmin(admin.ModelAdmin):
    list_display = (
        'nom',
        'prix_base',           # Champ réel → pour édition
        'prix_formate',        # $15
        'capacite_adultes',
        'capacite_enfants',
        'superficie',          # Champ réel → pour édition
        'superficie_formate',  # 18 m²
    )
    list_filter = ('capacite_adultes', 'capacite_enfants')
    search_fields = ('nom', 'description', 'equipements')
    ordering = ('prix_base',)

    # Édition rapide sur les CHAMPS RÉELS uniquement
    list_editable = ('prix_base', 'capacite_adultes', 'capacite_enfants', 'superficie')

    # === PRIX : $15 (sans .00) ===
    def prix_formate(self, obj):
        prix = obj.prix_base
        if prix is not None:
            if prix == prix.to_integral_value():
                valeur = int(prix)
            else:
                valeur = f"{prix:.2f}"
            return format_html('<strong style="color:green;">${}</strong>', valeur)
        return "-"
    prix_formate.short_description = 'Prix'
    prix_formate.admin_order_field = 'prix_base'

    # === SUPERFICIE : 18 m² (sans .00) ===
    def superficie_formate(self, obj):
        sup = obj.superficie
        if sup is not None:
            if sup == sup.to_integral_value():
                valeur = int(sup)
            else:
                valeur = f"{sup:.2f}"
            return format_html('<span style="font-weight:500;">{} m²</span>', valeur)
        return "-"
    superficie_formate.short_description = 'Superficie'
    superficie_formate.admin_order_field = 'superficie'

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

@admin.register(Chambre)
class ChambreAdmin(admin.ModelAdmin):
    list_display = ('numero', 'type_chambre', 'etage', 'statut')
    list_filter = ('statut', 'etage', 'type_chambre')
    search_fields = ('numero', 'type_chambre__nom')
    ordering = ('numero',)

@admin.register(MaintenanceChambre)
class MaintenanceChambreAdmin(admin.ModelAdmin):
    list_display = ('chambre', 'statut', 'priorite', 'date_signalement')
    list_filter = ('statut', 'priorite')
    search_fields = ('chambre__numero', 'probleme')
