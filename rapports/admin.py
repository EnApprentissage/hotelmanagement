# reports/admin.py
from django.contrib import admin
from .models import DailyReport


@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ['date', 'taux_occupation', 'ca_total', 'adr', 'revpar']
    list_filter = ['date']
    search_fields = ['date']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'

    fieldsets = (
        ('Période', {'fields': ('date',)}),
        ('Occupation', {'fields': ('chambres_total', 'chambres_occupees', 'taux_occupation')}),
        ('Réservations', {'fields': ('reservations_nouvelles', 'reservations_annulees', 'no_show')}),
        ('Revenus', {'fields': ('ca_hebergement', 'ca_restauration', 'ca_bar', 'ca_autres', 'ca_total')}),
        ('Indicateurs', {'fields': ('adr', 'revpar')}),
        ('Clients', {'fields': ('clients_nouveaux', 'clients_recurrents')}),
        ('Métadonnées', {'fields': ('created_at', 'updated_at')}),
    )