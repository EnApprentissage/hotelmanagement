# resto_bar/admin.py
from django.contrib import admin
from .models import CategorieMenu, ProduitMenu, Table


@admin.register(CategorieMenu)
class CategorieMenuAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_service', 'ordre_affichage')
    list_filter = ('type_service',)
    search_fields = ('nom', 'description')
    ordering = ('type_service', 'ordre_affichage')


@admin.register(ProduitMenu)
class ProduitMenuAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie', 'prix', 'stock_actuel', 'type_service')
    list_filter = ('categorie', 'type_service')
    search_fields = ('nom', 'description')
    ordering = ('nom',)


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('numero', 'type_service', 'capacite', 'statut')
    list_filter = ('type_service', 'statut')
    search_fields = ('numero',)
    ordering = ('numero',)