# chambres/views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.db.models import Q, Count
import json

from hotel_management_system.base_views import BaseAjaxCreateView, BaseAjaxUpdateView, BaseAjaxDeleteView
from .models import Chambre, TypeChambre
from .forms import ChambreForm
from .models import MaintenanceChambre


class ChambreListView(LoginRequiredMixin, ListView):
    model = Chambre
    template_name = 'chambres/chambre_list.html'
    context_object_name = 'chambres'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('type_chambre')
        
        # Filtres
        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        
        etage = self.request.GET.get('etage')
        if etage:
            queryset = queryset.filter(etage=etage)
        
        type_id = self.request.GET.get('type')
        if type_id:
            queryset = queryset.filter(type_chambre_id=type_id)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(numero__icontains=search) |
                Q(type_chambre__nom__icontains=search)
            )
        
        return queryset.order_by('numero')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques
        total_chambres = Chambre.objects.all()
        context['stats'] = {
            'disponibles': total_chambres.filter(statut='disponible').count(),
            'occupees': total_chambres.filter(statut='occupee').count(),
            'reservees': total_chambres.filter(statut='reservee').count(),
            'a_nettoyer': total_chambres.filter(statut='sale').count(),
        }
        
        # Types de chambres pour le filtre
        context['types_chambres'] = TypeChambre.objects.all()
        
        # Étages uniques pour le filtre
        context['etages'] = Chambre.objects.values_list('etage', flat=True).distinct().order_by('etage')
        
        return context


class ChambreDetailView(LoginRequiredMixin, DetailView):
    model = Chambre
    template_name = 'chambres/chambre_detail.html'
    context_object_name = 'chambre'


class ChambreCreateView(BaseAjaxCreateView):
    model = Chambre
    form_class = ChambreForm
    template_name = 'chambres/chambre_create.html'
    success_url = reverse_lazy('chambres:chambre_list')
    
    def get(self, request, *args, **kwargs):
        form = self.get_form()
        html = render_to_string(
            self.template_name,
            {'form': form},
            request=request
        )
        return JsonResponse({'html_form': html})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        chambre = form.save(commit=False)
        chambre.created_by = self.request.user
        chambre.save()
        
        return JsonResponse({
            'form_is_valid': True,
            'success': True,
            'message': f'Chambre {chambre.numero} créée avec succès !'
        })

    def form_invalid(self, form):
        html = render_to_string(
            self.template_name,
            {'form': form},
            request=self.request
        )
        return JsonResponse({
            'form_is_valid': False,
            'html_form': html
        })


class ChambreUpdateView(BaseAjaxUpdateView):
    model = Chambre
    form_class = ChambreForm
    template_name = 'chambres/chambre_update.html'
    success_url = reverse_lazy('chambres:chambre_list')
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        html = render_to_string(
            self.template_name,
            {'form': form, 'object': self.object},
            request=request
        )
        return JsonResponse({'html_form': html})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        chambre = form.save()
        return JsonResponse({
            'form_is_valid': True,
            'success': True,
            'message': f'Chambre {chambre.numero} modifiée avec succès !'
        })

    def form_invalid(self, form):
        html = render_to_string(
            self.template_name,
            {'form': form, 'object': self.object},
            request=self.request
        )
        return JsonResponse({
            'form_is_valid': False,
            'html_form': html
        })


class ChambreDeleteView(BaseAjaxDeleteView):
    model = Chambre
    success_url = reverse_lazy('chambres:chambre_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Vérifier si la chambre a des réservations
        if self.object.reservations.exists():
            return JsonResponse({
                'success': False,
                'error': f'Impossible de supprimer la Chambre {self.object.numero} : elle a des réservations associées.'
            })
        
        numero = self.object.numero
        self.object.delete()
        
        return JsonResponse({
            'form_is_valid': True,
            'success': True,
            'message': f'Chambre {numero} supprimée avec succès.'
        })


# ========================================
# MISE À JOUR DU STATUT DE NETTOYAGE
# ========================================
@login_required
@require_POST
def update_chambre_status(request, pk):
    """
    Vue AJAX pour mettre à jour le statut d'une chambre
    Utilisé pour les actions de nettoyage
    """
    try:
        chambre = get_object_or_404(Chambre, pk=pk)
        
        # Récupérer les données JSON
        data = json.loads(request.body)
        new_statut = data.get('statut')
        
        # Vérifier que le statut est valide
        statuts_valides = ['disponible', 'occupee', 'reservee', 'sale', 
                          'en_nettoyage', 'propre', 'maintenance', 'hors_service']
        
        if new_statut not in statuts_valides:
            return JsonResponse({
                'success': False,
                'error': 'Statut invalide'
            })
        
        # Logique métier selon le changement de statut
        ancien_statut = chambre.statut
        
        # Sale → En nettoyage
        if ancien_statut == 'sale' and new_statut == 'en_nettoyage':
            chambre.statut = 'en_nettoyage'
            chambre.save(update_fields=['statut'])
            message = f'Nettoyage de la Chambre {chambre.numero} commencé'
        
        # En nettoyage → Propre
        elif ancien_statut == 'en_nettoyage' and new_statut == 'propre':
            chambre.statut = 'propre'
            chambre.save(update_fields=['statut'])
            message = f'Chambre {chambre.numero} marquée comme propre'
            
            # Si la chambre n'est pas occupée/réservée, la rendre disponible
            if not chambre.reservations.filter(statut__in=['en_cours', 'confirmee']).exists():
                chambre.statut = 'disponible'
                chambre.save(update_fields=['statut'])
                message = f'Chambre {chambre.numero} propre et disponible'
        
        # Autres changements de statut
        else:
            chambre.statut = new_statut
            chambre.save(update_fields=['statut'])
            message = f'Statut de la Chambre {chambre.numero} mis à jour'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'new_statut': chambre.statut,
            'new_statut_display': chambre.get_statut_display()
        })
    
    except Chambre.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Chambre introuvable'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


# ========================================
# VUE POUR LE PERSONNEL DE MÉNAGE
# ========================================
@login_required
def chambres_a_nettoyer(request):
    """
    Vue spéciale pour le personnel de ménage
    Affiche uniquement les chambres à nettoyer et en cours de nettoyage
    """
    chambres_sales = Chambre.objects.filter(
        statut='sale'
    ).select_related('type_chambre').order_by('numero')
    
    chambres_en_cours = Chambre.objects.filter(
        statut='en_nettoyage'
    ).select_related('type_chambre').order_by('numero')
    
    chambres_propres = Chambre.objects.filter(
        statut='propre'
    ).select_related('type_chambre').order_by('numero')
    
    context = {
        'chambres_sales': chambres_sales,
        'chambres_en_cours': chambres_en_cours,
        'chambres_propres': chambres_propres,
        'total_a_nettoyer': chambres_sales.count(),
    }
    
    return render(request, 'chambres/chambres_nettoyage.html', context)




# ===============================
# LISTE DES MAINTENANCES (lecture seule)
# ===============================
@login_required
def maintenance_list(request):
    maintenances = MaintenanceChambre.objects.select_related(
        'chambre',
        'signale_par',
        'technicien'
    ).all()

    # Filtres
    search = request.GET.get('search')
    statut = request.GET.get('statut')

    if search:
        maintenances = maintenances.filter(
            Q(chambre__numero__icontains=search) |
            Q(probleme__icontains=search)
        )

    if statut:
        maintenances = maintenances.filter(statut=statut)

    # Stats
    stats = MaintenanceChambre.objects.values('statut').annotate(total=Count('id'))
    stats_dict = {s['statut']: s['total'] for s in stats}

    context = {
        'maintenances': maintenances,
        'statuts': MaintenanceChambre.STATUT_CHOICES,
        'stats': stats_dict,
        'search': search
    }
    return render(request, 'chambres/maintenance_list.html', context)


# ===============================
# DETAIL D'UNE MAINTENANCE
# ===============================
@login_required
def maintenance_detail(request, pk):
    maintenance = get_object_or_404(MaintenanceChambre, pk=pk)

    return render(request, 'chambres/maintenance_detail.html', {
        'maintenance': maintenance
    })