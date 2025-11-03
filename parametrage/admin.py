from django.contrib import admin
from django.utils.html import format_html
from .models import GlobalVariables


@admin.register(GlobalVariables)
class GlobalVariablesAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les variables globales de l'application.
    """
    
    # Colonnes affichées dans la liste
    list_display = (
        'colored_group',
        'cle',
        'valeur_preview',
        'valeur',
        'description_preview',
        'created_at_display'
    )
    
    # Filtres latéraux
    list_filter = ('group',)
    
    # Barre de recherche
    search_fields = ('group', 'cle', 'valeur', 'description')
    
    # Champs modifiables directement dans la liste
    list_editable = ('valeur',)
    
    # Nombre d'éléments par page
    list_per_page = 25
    
    # Organisation des champs dans le formulaire
    fieldsets = (
        ('Identification', {
            'fields': ('group', 'cle')
        }),
        ('Contenu', {
            'fields': ('valeur', 'description'),
            'classes': ('wide',)
        }),
    )
    
    # Champs en lecture seule (si vous ajoutez des timestamps)
    # readonly_fields = ('created_at', 'updated_at')
    
    # Ordre par défaut
    ordering = ('group', 'cle')
    
    # Actions personnalisées
    actions = ['duplicate_variable', 'export_as_json']
    
    def colored_group(self, obj):
        """
        Affiche le groupe avec une couleur selon le type.
        """
        colors = {
            'hotel': '#3498db',      # Bleu
            'entreprise': '#e74c3c',  # Rouge
            'system': '#95a5a6',      # Gris
            'paiement': '#2ecc71',    # Vert
            'notification': '#f39c12' # Orange
        }
        color = colors.get(obj.group, '#34495e')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.group.upper()
        )
    colored_group.short_description = 'Groupe'
    colored_group.admin_order_field = 'group'
    
    def valeur_preview(self, obj):
        """
        Affiche un aperçu de la valeur (tronquée si trop longue).
        """
        max_length = 50
        if len(obj.valeur) > max_length:
            return format_html(
                '<span title="{}">{} <em style="color: #7f8c8d;">...</em></span>',
                obj.valeur,
                obj.valeur[:max_length]
            )
        return obj.valeur
    valeur_preview.short_description = 'Valeur'
    
    def description_preview(self, obj):
        """
        Affiche un aperçu de la description.
        """
        max_length = 60
        if len(obj.description) > max_length:
            return format_html(
                '<span title="{}" style="color: #7f8c8d; font-style: italic;">{} ...</span>',
                obj.description,
                obj.description[:max_length]
            )
        return format_html(
            '<span style="color: #7f8c8d; font-style: italic;">{}</span>',
            obj.description
        )
    description_preview.short_description = 'Description'
    
    def created_at_display(self, obj):
        """
        Affiche la date de création (si le champ existe).
        Décommenter si vous ajoutez un champ created_at au modèle.
        """
        # if hasattr(obj, 'created_at') and obj.created_at:
        #     return obj.created_at.strftime('%d/%m/%Y %H:%M')
        return '-'
    created_at_display.short_description = 'Créé le'
    
    def duplicate_variable(self, request, queryset):
        """
        Action pour dupliquer une variable globale.
        """
        for var in queryset:
            var.pk = None
            var.cle = f"{var.cle}_copie"
            var.save()
        self.message_user(request, f"{queryset.count()} variable(s) dupliquée(s) avec succès.")
    duplicate_variable.short_description = "Dupliquer les variables sélectionnées"
    
    def export_as_json(self, request, queryset):
        """
        Exporter les variables sélectionnées en JSON.
        """
        import json
        from django.http import HttpResponse
        
        data = []
        for var in queryset:
            data.append({
                'group': var.group,
                'cle': var.cle,
                'valeur': var.valeur,
                'description': var.description
            })
        
        response = HttpResponse(
            json.dumps(data, indent=2, ensure_ascii=False),
            content_type='application/json'
        )
        response['Content-Disposition'] = 'attachment; filename="variables_globales.json"'
        return response
    export_as_json.short_description = "Exporter en JSON"
    
    def get_queryset(self, request):
        """
        Optimise les requêtes si nécessaire.
        """
        qs = super().get_queryset(request)
        return qs.select_related() if hasattr(qs, 'select_related') else qs
    
    def has_delete_permission(self, request, obj=None):
        """
        Restreint la suppression aux superutilisateurs uniquement.
        """
        return request.user.is_superuser
    
    class Media:
        """
        Ajoute du CSS/JS personnalisé si nécessaire.
        """
        css = {
            'all': ('admin/css/custom_global_variables.css',)
        }