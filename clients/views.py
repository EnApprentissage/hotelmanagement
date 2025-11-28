# clients/views.py
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils import timezone
from datetime import date
from hotel_management_system.base_views import BaseAjaxCreateView, BaseAjaxDeleteView, BaseAjaxUpdateView

from .models import Client, HistoriqueClient
from .forms import ClientForm, HistoriqueClientForm


# === CLIENT LIST VIEW ===
class ClientListView(ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    paginate_by = 15
    ordering = ['nom']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '').strip()
        
        if search:
            queryset = queryset.filter(
                Q(nom__icontains=search) |
                Q(prenom__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search) |
                Q(adresse__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context

# === CLIENT DETAIL VIEW ===
class ClientDetailView(DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = self.get_object()
        context['reservations'] = client.reservations.all()
        context['is_manager'] = self.request.user.is_staff or self.request.user.is_superuser
        return context

# === CLIENT CREATE VIEW ===
class ClientCreateView(BaseAjaxCreateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/client_create.html"
    success_url = reverse_lazy("clients:client_list")
    success_message = _("Client créé avec succès")

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        html_form = render_to_string(
            self.template_name,
            {"form": form},
            request=request
        )
        return JsonResponse({"html_form": html_form})

    def post(self, request, *args, **kwargs):
        """Traiter la soumission AJAX"""
        self.object = None
        form = self.get_form_class()(request.POST, request.FILES)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


    def form_valid(self, form):
        """Sauvegarde finale"""
        try:
            print("=== form_valid EMPLOYE CREATE ===")

            instance = form.save(commit=False)
            instance.user_id = self.request.user.id
            instance.save()

            print(f"client créé: {instance.nom} {instance.prenom}")

            return JsonResponse({
                'form_is_valid': True,
                'success': True
            })

        except Exception as e:
            print("ERREUR :", e)
            form.add_error(None, f"Erreur lors de la création : {e}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Retourner le formulaire avec erreurs - même format que Conge/Incident"""
        print("=== form_invalid EMPLOYE CREATE ===")
        print("Erreurs:", form.errors)

        html_form = render_to_string(
            self.template_name,
            {'form': form},
            request=self.request
        )

        return JsonResponse({
            'form_is_valid': False,
            'success': False,
            'html_form': html_form
        })
    
# === CLIENT UPDATE VIEW ===

class ClientUpdateView(BaseAjaxUpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_update.html'
    success_url = reverse_lazy('clients:client_list')
    success_message = _('Client mis à jour avec succès')

    def get_object(self):
        return get_object_or_404(Client, pk=self.kwargs['pk'])

    def dispatch(self, request, *args, **kwargs):
        """Gérer les différents cas de verrouillage"""
        client = self.get_object()
        is_manager = request.user.is_staff or request.user.is_superuser
        
        # Si verrouillé et que ce n'est PAS un manager
        if client.is_locked and not is_manager:
            if request.method == 'GET':
                return JsonResponse({
                    'html_form': self.get_locked_form_html(client),
                    'is_locked': True
                })
            else:
                return JsonResponse({
                    'form_is_valid': False,
                    'success': False,
                    'error': '🔒 Cette fiche est verrouillée. Seul un manager peut la déverrouiller.',
                    'is_locked': True
                })
        
        return super().dispatch(request, *args, **kwargs)

    def get_locked_form_html(self, client):
        """Générer un formulaire verrouillé en lecture seule"""
        html = f"""
        <div class="modal-header bg-warning text-white">
            <h5 class="modal-title">
                <i class="fas fa-lock"></i> Fiche Client Verrouillée
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
            <div class="alert alert-warning">
                <i class="fas fa-lock me-2"></i>
                <strong>Cette fiche est verrouillée</strong> et ne peut plus être modifiée.
                <br><small>Seul un manager peut la déverrouiller.</small>
            </div>
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label fw-bold">Civilité</label>
                    <p class="form-control-plaintext">{client.get_civilite_display()}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Nom Complet</label>
                    <p class="form-control-plaintext">{client.nom_complet}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Email</label>
                    <p class="form-control-plaintext">{client.email or '—'}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Téléphone</label>
                    <p class="form-control-plaintext">{client.phone}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Ville</label>
                    <p class="form-control-plaintext">{client.ville or '—'}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Pays</label>
                    <p class="form-control-plaintext">{client.pays or '—'}</p>
                </div>
            </div>
        </div>
        <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                <i class="fas fa-times"></i> Fermer
            </button>
        </div>
        """
        return html

    def get_form_context(self):
        """Ajouter is_manager au contexte"""
        return {
            'is_manager': self.request.user.is_staff or self.request.user.is_superuser  
        }

    def post(self, request, *args, **kwargs):
        """Soumission AJAX du formulaire"""
        self.object = self.get_object()
        is_manager = request.user.is_staff or request.user.is_superuser
        
        print("=== POST ClientUpdateView ===")
        print("POST data:", request.POST)
        print("Is Manager:", is_manager)

        # 🔓 DÉVERROUILLER (Manager uniquement)
        if 'unlock' in request.POST:
            print("=== DÉVERROUILLAGE DÉTECTÉ ===")
            
            if not is_manager:
                return JsonResponse({
                    'form_is_valid': False,
                    'success': False,
                    'error': '❌ Seul un manager peut déverrouiller cette fiche.'
                })
            
            self.object.is_locked = False
            self.object.save(update_fields=['is_locked'])
            
            HistoriqueClient.objects.create(
                client=self.object,
                type='unlock',
                description=f"Fiche déverrouillée par {request.user.get_full_name()}"
            )
            
            print(f"=== Client {self.object.pk} déverrouillé ===")
            
            return JsonResponse({
                'form_is_valid': True,
                'success': True,
                'unlocked': True,
                'message': f'🔓 Fiche de {self.object.nom_complet} déverrouillée avec succès.',
            })

        # 🔒 VERROUILLER
        if 'validate_lock' in request.POST:
            print("=== VERROUILLAGE DÉTECTÉ ===")
            
            self.object.is_locked = True
            self.object.save(update_fields=['is_locked'])
            
            HistoriqueClient.objects.create(
                client=self.object,
                type='lock',
                description=f"Fiche verrouillée par {request.user.get_full_name()}"
            )
            
            print(f"=== Client {self.object.pk} verrouillé ===")
            
            return JsonResponse({
                'form_is_valid': True,
                'success': True,
                'locked': True,
                'message': f'🔒 Fiche de {self.object.nom_complet} verrouillée avec succès.',
            })

        # MISE À JOUR NORMALE
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            print("Erreurs formulaire:", form.errors)
            return self.form_invalid(form)

    def form_valid(self, form):
        """Sauvegarder modifications et historique"""
        instance = form.save()
        
        HistoriqueClient.objects.create(
            client=instance,
            type='update',
            description=f"Fiche modifiée par {self.request.user.get_full_name()}"
        )
        
        print(f"=== Client {instance.pk} mis à jour ===")
        
        return JsonResponse({
            'form_is_valid': True,
            'success': True,
            'message': self.success_message
        })

    def form_invalid(self, form):
        """Retourner le formulaire avec erreurs"""
        html_form = render_to_string(
            self.template_name,
            {'form': form, 'object': self.object},
            request=self.request
        )
        
        return JsonResponse({
            'form_is_valid': False,
            'success': False,
            'html_form': html_form
        })

# === CLIENT DELETE VIEW ===
class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:client_list')

    def get(self, request, *args, **kwargs):
        """Charger la confirmation de suppression"""
        self.object = self.get_object()
        
        html_form = render_to_string(
            self.template_name,
            {'client': self.object}, 
            request=request
        )
        return JsonResponse({'html_form': html_form})

    def post(self, request, *args, **kwargs):
        """Supprimer le client"""
        self.object = self.get_object()
        self.object.delete()
        
        data = {
            'form_is_valid': True,
            'success': True,
            'url_redirect': self.success_url
        }
        return JsonResponse(data)

# ==================== HISTORIQUE ====================
class HistoriqueListView(ListView):
    model = HistoriqueClient
    template_name = 'clients/historique_list.html'
    context_object_name = 'historiques'
    ordering = ['-date']


class HistoriqueCreateView(CreateView):
    model = HistoriqueClient
    form_class = HistoriqueClientForm
    template_name = 'clients/historique_form.html'
    success_url = reverse_lazy('clients:historique_list')


class HistoriqueUpdateView(UpdateView):
    model = HistoriqueClient
    form_class = HistoriqueClientForm
    template_name = 'clients/historique_form.html'
    success_url = reverse_lazy('clients:historique_list')


class HistoriqueDeleteView(DeleteView):
    model = HistoriqueClient
    template_name = 'clients/historique_confirm_delete.html'
    success_url = reverse_lazy('clients:historique_list')