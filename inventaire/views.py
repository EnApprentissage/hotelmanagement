# inventaire/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import (
    CategorieInventaire, Produit, MouvementStock, DemandeReapprovisionnement,
    LigneDemandeReapprovisionnement, InventairePhysique, LigneInventairePhysique,
    DotationChambre, Signalement
)
from .forms import (
    CategorieInventaireForm, ProduitForm, MouvementStockForm,
    DemandeReapproForm, LigneDemandeForm, InventairePhysiqueForm,
    LigneInventaireForm, DotationChambreForm, SignalementForm
)

# ---------- Catégories ----------
def categories_list(request):
    categories = CategorieInventaire.objects.all()
    paginator = Paginator(categories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'inventaire/categories_list.html', {'categories': page_obj})

def categorie_create(request):
    form = CategorieInventaireForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('categories_list')
    return render(request, 'inventaire/categorie_form.html', {'form': form})

def categorie_update(request, pk):
    categorie = get_object_or_404(CategorieInventaire, pk=pk)
    form = CategorieInventaireForm(request.POST or None, instance=categorie)
    if form.is_valid():
        form.save()
        return redirect('categories_list')
    return render(request, 'inventaire/categorie_form.html', {'form': form})

# ---------- Produits ----------
def produits_list(request):
    produits = Produit.objects.all()
    paginator = Paginator(produits, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'inventaire/produits_list.html', {'produits': page_obj})

def produit_create(request):
    form = ProduitForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('produits_list')
    return render(request, 'inventaire/produit_form.html', {'form': form})

def produit_update(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    form = ProduitForm(request.POST or None, request.FILES or None, instance=produit)
    if form.is_valid():
        form.save()
        return redirect('produits_list')
    return render(request, 'inventaire/produit_form.html', {'form': form})

# ---------- Mouvements ----------
def mouvements_list(request):
    mouvements = MouvementStock.objects.all().order_by('-date_mouvement')
    paginator = Paginator(mouvements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'inventaire/mouvements_list.html', {'mouvements': page_obj})

def mouvement_create(request):
    form = MouvementStockForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('mouvements_list')
    return render(request, 'inventaire/mouvement_form.html', {'form': form})

# ---------- Demandes de réappro ----------
def demandes_list(request):
    demandes = DemandeReapprovisionnement.objects.all()
    paginator = Paginator(demandes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'inventaire/demandes_list.html', {'demandes': page_obj})

def demande_create(request):
    form = DemandeReapproForm(request.POST or None)
    if form.is_valid():
        demande = form.save()
        return redirect('demandes_list')
    return render(request, 'inventaire/demande_form.html', {'form': form})

# ---------- Inventaire physique ----------
def inventaires_list(request):
    inventaires = InventairePhysique.objects.all()
    paginator = Paginator(inventaires, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'inventaire/inventaires_list.html', {'inventaires': page_obj})

def inventaire_create(request):
    form = InventairePhysiqueForm(request.POST or None)
    if form.is_valid():
        inventaire = form.save()
        return redirect('inventaires_list')
    return render(request, 'inventaire/inventaire_form.html', {'form': form})

# ---------- Dotations ----------
def dotations_list(request):
    dotations = DotationChambre.objects.all()
    paginator = Paginator(dotations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
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
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'inventaire/signalements_list.html', {'signalements': page_obj})

def signalement_create(request):
    form = SignalementForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('signalements_list')
    return render(request, 'inventaire/signalement_form.html', {'form': form})
