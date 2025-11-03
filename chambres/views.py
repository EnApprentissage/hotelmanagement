# chambres/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Chambre, MaintenanceChambre
from .forms import ChambreForm, MaintenanceChambreForm

# ===========================
# CHAMBRES
# ===========================
def liste_chambres(request):
    chambres = Chambre.objects.select_related('type_chambre').all()
    search = request.GET.get('q')
    if search:
        chambres = chambres.filter(
            Q(numero__icontains=search) |
            Q(type_chambre__nom__icontains=search) |
            Q(statut__icontains=search)
        )
    paginator = Paginator(chambres, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'chambres/liste_chambres.html', {'page_obj': page_obj})

def creer_chambre(request):
    form = ChambreForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Chambre créée avec succès.")
        return redirect('liste_chambres')
    return render(request, 'chambres/creer_chambre.html', {'form': form})

def modifier_chambre(request, pk):
    chambre = get_object_or_404(Chambre, pk=pk)
    form = ChambreForm(request.POST or None, instance=chambre)
    if form.is_valid():
        form.save()
        messages.success(request, "Chambre modifiée avec succès.")
        return redirect('liste_chambres')
    return render(request, 'chambres/modifier_chambre.html', {'form': form})

def detail_chambre(request, pk):
    chambre = get_object_or_404(Chambre, pk=pk)
    maintenances = chambre.maintenances.all()
    return render(request, 'chambres/detail_chambre.html', {'chambre': chambre, 'maintenances': maintenances})

# ===========================
# MAINTENANCES CHAMBRES
# ===========================
def liste_maintenances(request):
    maintenances = MaintenanceChambre.objects.select_related('chambre', 'signale_par', 'technicien').all()
    paginator = Paginator(maintenances, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'chambres/liste_maintenances.html', {'page_obj': page_obj})

def creer_maintenance(request):
    form = MaintenanceChambreForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Maintenance créée avec succès.")
        return redirect('liste_maintenances')
    return render(request, 'chambres/creer_maintenance.html', {'form': form})

def modifier_maintenance(request, pk):
    maintenance = get_object_or_404(MaintenanceChambre, pk=pk)
    form = MaintenanceChambreForm(request.POST or None, instance=maintenance)
    if form.is_valid():
        form.save()
        messages.success(request, "Maintenance modifiée avec succès.")
        return redirect('liste_maintenances')
    return render(request, 'chambres/modifier_maintenance.html', {'form': form})

def detail_maintenance(request, pk):
    maintenance = get_object_or_404(MaintenanceChambre, pk=pk)
    return render(request, 'chambres/detail_maintenance.html', {'maintenance': maintenance})
