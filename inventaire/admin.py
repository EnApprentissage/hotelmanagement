# inventaire/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import CategorieInventaire, Produit


@admin.register(CategorieInventaire)
class CategorieInventaireAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom', 'description')
    ordering = ('nom',)


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'nom', 'categorie',
        'stock_actuel', 'unite_mesure',
        'prix_formate',  # ← Nouvelle colonne formatée
        
    )
    list_filter = ('categorie', 'unite_mesure')
    search_fields = ('code', 'nom', 'description',)
    ordering = ('nom',)

    # Édition rapide du stock
    list_editable = ('stock_actuel',)

    fieldsets = (
        ('Informations générales', {
            'fields': ('code', 'nom', 'categorie', 'description')
        }),
        ('Stock', {
            'fields': ('stock_actuel', 'stock_minimum', 'stock_maximum', 'unite_mesure')
        }),
        ('Prix & Emplacement', {
            'fields': ('prix_unitaire', )  
        }),
    )

    # === AFFICHAGE DU PRIX AVEC $ ou FC ===
    def prix_formate(self, obj):
        prix = obj.prix_unitaire
        if prix is None:
            return "-"

        # Choisis ici : $ ou FC
        # Option 1 : Dollar US (ex: 15.50 → $15.50)
        # Option 2 : Franc Congolais (ex: 1500 → 1500 FC)

        # === OPTION 1 : $ (commentée) ===
        valeur = int(prix) if prix == prix.to_integral_value() else f"{prix:.2f}"
        return format_html('<strong style="color:green;">${}</strong>', valeur)

        # # === OPTION 2 : FC (actif) ===
        # valeur = int(prix) if prix == prix.to_integral_value() else f"{prix:,.0f}".replace(",", " ")
        # return format_html('<strong style="color:blue;">{} FC</strong>', valeur)

    prix_formate.short_description = 'Prix unitaire'
    prix_formate.admin_order_field = 'prix_unitaire'  # Permet le tri