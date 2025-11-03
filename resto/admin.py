# resto_bar/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import CategorieMenu, ProduitMenu, Table


@admin.register(CategorieMenu)
class CategorieMenuAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_service', 'ordre_affichage')
    list_filter = ('type_service',)
    search_fields = ('nom', 'description')
    ordering = ('type_service', 'ordre_affichage')


@admin.register(ProduitMenu)
class ProduitMenuAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie', 'prix_formate', 'stock_actuel', 'type_service')
    list_filter = ('categorie', 'type_service')
    search_fields = ('nom', 'description')
    ordering = ('nom',)

    # === AJOUT : PRIX AVEC $ ou FC ===
    def prix_formate(self, obj):
        prix = obj.prix
        if prix is None:
            return "-"

        # === CHOISIS ICI : $ ou FC ===
        # Option 1 : Dollar ($)
        return format_html('<strong style="color:green;">${}</strong>', int(prix) if prix == prix.to_integral_value() else f"{prix:.2f}")

        # Option 2 : Franc Congolais (FC) ← ACTIF
        # valeur = int(prix) if prix == prix.to_integral_value() else f"{prix:,.0f}".replace(",", " ")
        # return format_html('<strong style="color:#e67e22;">{} FC</strong>', valeur)

    prix_formate.short_description = 'Prix'
    prix_formate.admin_order_field = 'prix'  # Permet le tri


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('numero', 'type_service', 'capacite', 'statut')
    list_filter = ('type_service', 'statut')
    search_fields = ('numero',)
    ordering = ('numero',)