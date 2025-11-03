# inventaire/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import (
    MouvementStock, DemandeReapprovisionnement,
    InventairePhysique, DotationChambre, Signalement
)
from .forms import (
    MouvementStockForm, DemandeReapproForm,
    InventairePhysiqueForm, DotationChambreForm, SignalementForm
)

# ---------- Mouvements ----------
def mouvements_list(request):
    mouvements = MouvementStock.objects.all().order_by('-date_mouvement')
    paginator = Paginator(mouvements, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'inventaire/mouvements_list.html', {'mouvements': page_obj})

def mouvement_create(request):
    form = MouvementStockForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('mouvements_list')
    return render(request, 'inventaire/mouvement_form.html', {'form': form})

# ---------- Demandes de réappro ----------
def demandes_list(request):
    demandes = DemandeReapprovisionnement.objects.all().order_by('-date_demande')
    paginator = Paginator(demandes, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'inventaire/demandes_list.html', {'demandes': page_obj})

def demande_create(request):
    form = DemandeReapproForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('demandes_list')
    return render(request, 'inventaire/demande_form.html', {'form': form})

# ---------- Inventaires physiques ----------
def inventaires_list(request):
    inventaires = InventairePhysique.objects.all().order_by('-date_inventaire')
    paginator = Paginator(inventaires, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'inventaire/inventaires_list.html', {'inventaires': page_obj})

def inventaire_create(request):
    form = InventairePhysiqueForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('inventaires_list')
    return render(request, 'inventaire/inventaire_form.html', {'form': form})

# ---------- Dotations ----------
def dotations_list(request):
    dotations = DotationChambre.objects.all()
    paginator = Paginator(dotations, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'inventaire/dotations_list.html', {'dotations': page_obj})

def dotation_create(request):
    form = DotationChambreForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('dotations_list')
    return render(request, 'inventaire/dotation_form.html', {'form': form})

# ---------- Signalements ----------
def signalements_list(request):
    signalements = Signalement.objects.all().order_by('-date_signalement')
    paginator = Paginator(signalements, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'inventaire/signalements_list.html', {'signalements': page_obj})

def signalement_create(request):
    form = SignalementForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('signalements_list')
    return render(request, 'inventaire/signalement_form.html', {'form': form})
