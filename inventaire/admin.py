# inventaire/admin.py
from django.contrib import admin
from .models import CategorieInventaire, Produit

@admin.register(CategorieInventaire)
class CategorieInventaireAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom', 'description')
    ordering = ('nom',)

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'nom', 'categorie', 'stock_actuel',
        'stock_minimum', 'stock_maximum', 'prix_unitaire', 'unite_mesure'
    )
    list_filter = ('categorie', 'unite_mesure')
    search_fields = ('code', 'nom', 'description', 'emplacement')
    ordering = ('nom',)

    # Permet de modifier le stock rapidement depuis la liste
    list_editable = ('stock_actuel',)

    fieldsets = (
        ('Informations générales', {
            'fields': ('code', 'nom', 'categorie', 'description')
        }),
        ('Stock', {
            'fields': ('stock_actuel', 'stock_minimum', 'stock_maximum', 'unite_mesure')
        }),
        ('Prix & Emplacement', {
            'fields': ('prix_unitaire', 'emplacement')
        }),
    )
