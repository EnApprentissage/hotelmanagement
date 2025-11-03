# resto_bar/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import CategorieMenu, ProduitMenu, Table, Commande, CommandeItem
from .forms import (
    CategorieMenuForm, ProduitMenuForm, TableForm,
    CommandeForm, CommandeItemForm
)

# ---------- Catégories ----------
def categories_list(request):
    categories = CategorieMenu.objects.all()
    paginator = Paginator(categories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'resto_bar/categories_list.html', {'categories': page_obj})

def categorie_create(request):
    form = CategorieMenuForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('categories_list')
    return render(request, 'resto_bar/categorie_form.html', {'form': form})

def categorie_update(request, pk):
    categorie = get_object_or_404(CategorieMenu, pk=pk)
    form = CategorieMenuForm(request.POST or None, instance=categorie)
    if form.is_valid():
        form.save()
        return redirect('categories_list')
    return render(request, 'resto_bar/categorie_form.html', {'form': form})

# ---------- Produits ----------
def produits_list(request):
    produits = ProduitMenu.objects.all()
    paginator = Paginator(produits, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'resto_bar/produits_list.html', {'produits': page_obj})

def produit_create(request):
    form = ProduitMenuForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('produits_list')
    return render(request, 'resto_bar/produit_form.html', {'form': form})

def produit_update(request, pk):
    produit = get_object_or_404(ProduitMenu, pk=pk)
    form = ProduitMenuForm(request.POST or None, request.FILES or None, instance=produit)
    if form.is_valid():
        form.save()
        return redirect('produits_list')
    return render(request, 'resto_bar/produit_form.html', {'form': form})

# ---------- Tables ----------
def tables_list(request):
    tables = Table.objects.all()
    paginator = Paginator(tables, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'resto_bar/tables_list.html', {'tables': page_obj})

def table_create(request):
    form = TableForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('tables_list')
    return render(request, 'resto_bar/table_form.html', {'form': form})

def table_update(request, pk):
    table = get_object_or_404(Table, pk=pk)
    form = TableForm(request.POST or None, instance=table)
    if form.is_valid():
        form.save()
        return redirect('tables_list')
    return render(request, 'resto_bar/table_form.html', {'form': form})

# ---------- Commandes ----------
def commandes_list(request):
    commandes = Commande.objects.all().order_by('-date_commande')
    paginator = Paginator(commandes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'resto_bar/commandes_list.html', {'commandes': page_obj})

def commande_create(request):
    form = CommandeForm(request.POST or None)
    if form.is_valid():
        commande = form.save()
        return redirect('commandes_list')
    return render(request, 'resto_bar/commande_form.html', {'form': form})

def commande_detail(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    items = commande.items.all()
    return render(request, 'resto_bar/commande_detail.html', {'commande': commande, 'items': items})
