# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from accounts.forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Administration personnalisée pour le modèle User
    """
    # === Formulaire de création et modification ===
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    # === Affichage dans la liste des utilisateurs ===
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'role', 'phone',
        'is_active_employee', 'is_staff', 'is_superuser', 'date_joined'
    )
    list_filter = (
        'role', 'is_active_employee', 'is_staff', 'is_superuser',
        'date_joined', 'last_login'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)

    # === Organisation des champs dans le formulaire de modification ===
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Informations personnelles'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar', 'avatar_preview')}),
        (_('Rôle & Statut'), {'fields': ('role', 'is_active_employee')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Dates importantes'), {'fields': ('last_login', 'date_joined'), 'classes': ('collapse',)}),
    )

    # === Organisation des champs dans le formulaire de création ===
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'phone', 'role', 'password1', 'password2'),
        }),
        (_('Statut employé'), {
            'fields': ('is_active_employee',),
            'description': _('Cochez si cet utilisateur est un employé actif.')
        }),
    )

    # === Champs en lecture seule ===
    readonly_fields = ('date_joined', 'last_login', 'avatar_preview')

    # === Aperçu de l'avatar ===
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 50%;">',
                obj.avatar.url
            )
        return "(Aucun avatar)"
    avatar_preview.short_description = 'Aperçu Avatar'

    # === Filtre horizontal pour les groupes et permissions ===
    filter_horizontal = ('groups', 'user_permissions',)

    # === Actions personnalisées ===
    actions = ['make_active_employee', 'make_inactive_employee']

    def make_active_employee(self, request, queryset):
        # Limiter aux superusers
        if not request.user.is_superuser:
            self.message_user(request, "Seuls les superusers peuvent modifier le statut des employés.", level='error')
            return
        queryset.update(is_active_employee=True)
        self.message_user(request, "Les utilisateurs sélectionnés sont maintenant marqués comme employés actifs.")
    make_active_employee.short_description = "Marquer comme employé actif"

    def make_inactive_employee(self, request, queryset):
        if not request.user.is_superuser:
            self.message_user(request, "Seuls les superusers peuvent modifier le statut des employés.", level='error')
            return
        queryset.update(is_active_employee=False)
        self.message_user(request, "Les utilisateurs sélectionnés sont maintenant marqués comme employés inactifs.")
    make_inactive_employee.short_description = "Marquer comme employé inactif"
