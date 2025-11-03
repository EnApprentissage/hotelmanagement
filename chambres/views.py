# chambres/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import TypeChambre, Chambre, MaintenanceChambre
from .forms import ChambreForm, TypeChambreForm, MaintenanceChambreForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

# ===========================
# TYPE DE CHAMBRES
# ===========================
def liste_types_chambres(request):
    types_chambres = TypeChambre.objects.all()
    paginator = Paginator(types_chambres, 10)  # 10 par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'chambres/liste_types_chambres.html', {'page_obj': page_obj})


def creer_type_chambre(request):
    if request.method == 'POST':
        form = TypeChambreForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Type de chambre créé avec succès.")
            return redirect('liste_types_chambres')
    else:
        form = TypeChambreForm()
    return render(request, 'chambres/creer_type_chambre.html', {'form': form})


def modifier_type_chambre(request, pk):
    type_chambre = get_object_or_404(TypeChambre, pk=pk)
    if request.method == 'POST':
        form = TypeChambreForm(request.POST, request.FILES, instance=type_chambre)
        if form.is_valid():
            form.save()
            messages.success(request, "Type de chambre modifié avec succès.")
            return redirect('liste_types_chambres')
    else:
        form = TypeChambreForm(instance=type_chambre)
    return render(request, 'chambres/modifier_type_chambre.html', {'form': form})


def supprimer_type_chambre(request, pk):
    type_chambre = get_object_or_404(TypeChambre, pk=pk)
    type_chambre.delete()
    messages.success(request, "Type de chambre supprimé.")
    return redirect('liste_types_chambres')


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
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'chambres/liste_chambres.html', {'page_obj': page_obj})


def creer_chambre(request):
    if request.method == 'POST':
        form = ChambreForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Chambre créée avec succès.")
            return redirect('liste_chambres')
    else:
        form = ChambreForm()
    return render(request, 'chambres/creer_chambre.html', {'form': form})


def modifier_chambre(request, pk):
    chambre = get_object_or_404(Chambre, pk=pk)
    if request.method == 'POST':
        form = ChambreForm(request.POST, instance=chambre)
        if form.is_valid():
            form.save()
            messages.success(request, "Chambre modifiée avec succès.")
            return redirect('liste_chambres')
    else:
        form = ChambreForm(instance=chambre)
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
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'chambres/liste_maintenances.html', {'page_obj': page_obj})


def creer_maintenance(request):
    if request.method == 'POST':
        form = MaintenanceChambreForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Maintenance créée avec succès.")
            return redirect('liste_maintenances')
    else:
        form = MaintenanceChambreForm()
    return render(request, 'chambres/creer_maintenance.html', {'form': form})


def modifier_maintenance(request, pk):
    maintenance = get_object_or_404(MaintenanceChambre, pk=pk)
    if request.method == 'POST':
        form = MaintenanceChambreForm(request.POST, instance=maintenance)
        if form.is_valid():
            form.save()
            messages.success(request, "Maintenance modifiée avec succès.")
            return redirect('liste_maintenances')
    else:
        form = MaintenanceChambreForm(instance=maintenance)
    return render(request, 'chambres/modifier_maintenance.html', {'form': form})


def detail_maintenance(request, pk):
    maintenance = get_object_or_404(MaintenanceChambre, pk=pk)
    return render(request, 'chambres/detail_maintenance.html', {'maintenance': maintenance})
