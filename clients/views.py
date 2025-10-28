# clients/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Client, HistoriqueClient
from .forms import ClientForm, HistoriqueClientForm


# ==================== CLIENT ====================
class ClientListView(ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    ordering = ['-date_creation']


class ClientDetailView(DetailView):
    model = Client
    template_name = 'clients/client_detail.html'


class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')


class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:client_list')


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