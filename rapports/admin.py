from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import DailyReport


@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour le rapport journalier (DailyReport).
    Permet de consulter et d'ajouter/modifier les données.
    """

    # Colonnes visibles dans la liste
    list_display = (
        'date',
        'taux_occupation_formate',
        'ca_total_formate',
        'adr_formate',
        'revpar_formate'
    )

    # Filtres et recherche
    list_filter = ('date',)
    search_fields = ('date',)
    date_hierarchy = 'date'
    ordering = ('-date',)

    # Organisation du formulaire
    fieldsets = (
        ('Période', {'fields': ('date',)}),
        ('Occupation', {'fields': ('chambres_total', 'chambres_occupees', 'taux_occupation')}),
        ('Réservations', {'fields': ('reservations_nouvelles', 'reservations_annulees', 'no_show')}),
        ('Revenus', {'fields': ('ca_hebergement', 'ca_restauration', 'ca_bar', 'ca_total')}),
        ('Indicateurs', {'fields': ('adr', 'revpar')}),
        ('Clients', {'fields': ('clients_nouveaux', 'clients_recurrents')}),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    # === FORMATTAGE VISUEL ===

    def taux_occupation_formate(self, obj):
        if obj.taux_occupation is None:
            return "-"
        valeur = f"{obj.taux_occupation:.1f}"
        return format_html('<strong style="color:#27ae60;">{}%</strong>', valeur)
    taux_occupation_formate.short_description = 'Taux occ.'
    taux_occupation_formate.admin_order_field = 'taux_occupation'

    def ca_total_formate(self, obj):
        ca = obj.ca_total
        if not ca:
            return "-"
        valeur = f"{ca:,.0f}".replace(",", " ")
        return format_html('<strong style="color:green;">${}</strong>', valeur)
    ca_total_formate.short_description = 'CA Total'
    ca_total_formate.admin_order_field = 'ca_total'

    def adr_formate(self, obj):
        adr = obj.adr
        if not adr:
            return "-"
        valeur = f"{adr:,.0f}".replace(",", " ")
        return format_html('<span style="color:#2980b9;">${}</span>', valeur)
    adr_formate.short_description = 'ADR'
    adr_formate.admin_order_field = 'adr'

    def revpar_formate(self, obj):
        revpar = obj.revpar
        if not revpar:
            return "-"
        valeur = f"{revpar:,.0f}".replace(",", " ")
        return format_html('<span style="color:#8e44ad;">${}</span>', valeur)
    revpar_formate.short_description = 'RevPAR'
    revpar_formate.admin_order_field = 'revpar'

    # === Permissions ===
    # Ici, on autorise tout (ajout, modification, suppression)
    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True
