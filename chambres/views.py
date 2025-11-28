# chambres/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import Chambre, MaintenanceChambre, TypeChambre
from .forms import ChambreForm, MaintenanceChambreForm

# ===========================
# CHAMBRES
# ===========================
@login_required
def chambre_list(request):
    """Liste des chambres avec filtres et statistiques"""
    chambres = Chambre.objects.select_related('type_chambre').all()
    
    # Filtres
    search = request.GET.get('search')
    statut = request.GET.get('statut')
    etage = request.GET.get('etage')
    type_id = request.GET.get('type')
    
    if search:
        chambres = chambres.filter(
            Q(numero__icontains=search) |
            Q(type_chambre__nom__icontains=search)
        )
    
    if statut:
        chambres = chambres.filter(statut=statut)
    
    if etage:
        chambres = chambres.filter(etage=etage)
    
    if type_id:
        chambres = chambres.filter(type_chambre_id=type_id)
    
    # Statistiques par statut
    stats = Chambre.objects.values('statut').annotate(count=Count('id'))
    stats_dict = {item['statut']: item['count'] for item in stats}
    
    # Étages et types disponibles pour les filtres
    etages = Chambre.objects.values_list('etage', flat=True).distinct().order_by('etage')
    types_chambres = TypeChambre.objects.all()
    
    # Pagination
    paginator = Paginator(chambres, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'stats': stats_dict,
        'etages': etages,
        'types_chambres': types_chambres,
        'statuts': Chambre.STATUT_CHOICES,
    }
    return render(request, 'chambres/chambre_list.html', context)


@login_required
def chambre_update(request, pk):
    """Modifier une chambre via AJAX"""
    chambre = get_object_or_404(Chambre, pk=pk)
    
    if request.method == 'GET':
        form = ChambreForm(instance=chambre)
        html_form = render_to_string(
            'chambres/chambre_update.html',
            {'form': form, 'object': chambre},
            request=request
        )
        return JsonResponse({'html_form': html_form})
    
    elif request.method == 'POST':
        form = ChambreForm(request.POST, instance=chambre)
        if form.is_valid():
            chambre = form.save()
            return JsonResponse({
                'form_is_valid': True,
                'success': True,
                'message': f'Chambre {chambre.numero} modifiée avec succès.'
            })
        else:
            html_form = render_to_string(
                'chambres/chambre_update.html',
                {'form': form, 'object': chambre},
                request=request
            )
            return JsonResponse({'html_form': html_form})


@login_required
def chambre_delete(request, pk):
    """Supprimer une chambre via AJAX"""
    chambre = get_object_or_404(Chambre, pk=pk)
    
    if request.method == 'POST':
        # Vérifier si la chambre peut être supprimée
        if chambre.statut in ['occupee', 'reservee']:
            return JsonResponse({
                'success': False,
                'error': 'Impossible de supprimer une chambre occupée ou réservée.'
            })
        
        numero = chambre.numero
        chambre.delete()
        return JsonResponse({
            'form_is_valid': True,
            'success': True,
            'message': f'Chambre {numero} supprimée avec succès.'
        })


@login_required
def chambre_status(request, pk):
    """Changer le statut d'une chambre rapidement"""
    chambre = get_object_or_404(Chambre, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('statut')
        
        if new_status in dict(Chambre.STATUT_CHOICES):
            old_status = chambre.get_statut_display()
            chambre.statut = new_status
            chambre.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Statut de la chambre {chambre.numero} changé de "{old_status}" à "{chambre.get_statut_display()}".'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Statut invalide.'
            })


@login_required
def chambre_detail(request, pk):
    """Détails d'une chambre"""
    chambre = get_object_or_404(Chambre, pk=pk)
    maintenances = chambre.maintenances.all()[:10]
    
    # Récupérer les réservations si le modèle existe
    try:
        reservations = chambre.reservations.all()[:10]
    except:
        reservations = []
    
    context = {
        'chambre': chambre,
        'maintenances': maintenances,
        'reservations': reservations,
    }
    return render(request, 'chambres/chambre_detail.html', context)


# ===========================
# MAINTENANCES CHAMBRES
# ===========================
@login_required
def liste_maintenances(request):
    """Liste des maintenances"""
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
    
    paginator = Paginator(maintenances, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'statuts': MaintenanceChambre.STATUT_CHOICES,
    }
    return render(request, 'chambres/liste_maintenances.html', context)


@login_required
def creer_maintenance(request):
    """Créer une maintenance"""
    form = MaintenanceChambreForm(request.POST or None)
    if form.is_valid():
        maintenance = form.save(commit=False)
        if request.user.is_authenticated:
            maintenance.signale_par = request.user
        maintenance.save()
        messages.success(request, "Maintenance créée avec succès.")
        return redirect('chambres:liste_maintenances')
    return render(request, 'chambres/creer_maintenance.html', {'form': form})


@login_required
def modifier_maintenance(request, pk):
    """Modifier une maintenance"""
    maintenance = get_object_or_404(MaintenanceChambre, pk=pk)
    form = MaintenanceChambreForm(request.POST or None, instance=maintenance)
    if form.is_valid():
        form.save()
        messages.success(request, "Maintenance modifiée avec succès.")
        return redirect('chambres:liste_maintenances')
    return render(request, 'chambres/modifier_maintenance.html', {'form': form})


@login_required
def detail_maintenance(request, pk):
    """Détails d'une maintenance"""
    maintenance = get_object_or_404(MaintenanceChambre, pk=pk)
    return render(request, 'chambres/detail_maintenance.html', {'maintenance': maintenance})