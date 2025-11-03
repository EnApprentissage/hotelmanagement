# resto_bar/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Commande, CommandeItem
from .forms import CommandeForm

# Liste des commandes
def commandes_list(request):
    commandes = Commande.objects.all().order_by('-date_commande')
    paginator = Paginator(commandes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'resto_bar/commandes_list.html', {'commandes': page_obj})

# Créer une nouvelle commande
def commande_create(request):
    form = CommandeForm(request.POST or None)
    if form.is_valid():
        commande = form.save()
        return redirect('commandes_list')
    return render(request, 'resto_bar/commande_form.html', {'form': form})

# Détail d'une commande
def commande_detail(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    items = commande.items.all()
    return render(request, 'resto_bar/commande_detail.html', {'commande': commande, 'items': items})
