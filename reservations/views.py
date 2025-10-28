# reservations/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Reservation
from .forms import ReservationForm


class ReservationListView(ListView):
    model = Reservation
    template_name = 'reservations/list.html'
    context_object_name = 'reservations'
    ordering = ['-date_creation']


class ReservationDetailView(DetailView):
    model = Reservation
    template_name = 'reservations/detail.html'


class ReservationCreateView(CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'reservations/form.html'
    success_url = reverse_lazy('reservations:list')


class ReservationUpdateView(UpdateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'reservations/form.html'
    success_url = reverse_lazy('reservations:list')


class ReservationDeleteView(DeleteView):
    model = Reservation
    template_name = 'reservations/confirm_delete.html'
    success_url = reverse_lazy('reservations:list')