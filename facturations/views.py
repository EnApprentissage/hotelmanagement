# facturation/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Facture, Paiement
from .forms import FactureForm, PaiementForm


# ==================== FACTURE ====================
class FactureListView(ListView):
    model = Facture
    template_name = 'facturation/facture_list.html'
    context_object_name = 'factures'
    ordering = ['-date_creation']


class FactureDetailView(DetailView):
    model = Facture
    template_name = 'facturation/facture_detail.html'


class FactureCreateView(CreateView):
    model = Facture
    form_class = FactureForm
    template_name = 'facturation/facture_form.html'
    success_url = reverse_lazy('facturation:facture_list')


class FactureUpdateView(UpdateView):
    model = Facture
    form_class = FactureForm
    template_name = 'facturation/facture_form.html'
    success_url = reverse_lazy('facturation:facture_list')


class FactureDeleteView(DeleteView):
    model = Facture
    template_name = 'facturation/facture_confirm_delete.html'
    success_url = reverse_lazy('facturation:facture_list')


# ==================== PAIEMENT ====================
class PaiementListView(ListView):
    model = Paiement
    template_name = 'facturation/paiement_list.html'
    context_object_name = 'paiements'
    ordering = ['-date_paiement']


class PaiementCreateView(CreateView):
    model = Paiement
    form_class = PaiementForm
    template_name = 'facturation/paiement_form.html'
    success_url = reverse_lazy('facturation:paiement_list')


class PaiementUpdateView(UpdateView):
    model = Paiement
    form_class = PaiementForm
    template_name = 'facturation/paiement_form.html'
    success_url = reverse_lazy('facturation:paiement_list')


class PaiementDeleteView(DeleteView):
    model = Paiement
    template_name = 'facturation/paiement_confirm_delete.html'
    success_url = reverse_lazy('facturation:paiement_list')