# reservations/views.py
from asyncio import events
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from hotel_management_system.base_views import BaseAjaxCreateView, BaseAjaxDeleteView, BaseAjaxUpdateView
from .models import Reservation
from clients.models import Client
from .forms import ReservationCreateForm
from django.views.decorators.http import require_GET

from datetime import timedelta



class ReservationListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'reservations/reservation_list.html'
    context_object_name = 'reservations'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtre par statut
        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        
        # Recherche
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(numero_reservation__icontains=search) |
                Q(client__nom__icontains=search) |
                Q(client__prenom__icontains=search) |
                Q(chambre__numero__icontains=search)
            )
        
        return queryset.select_related('client', 'chambre', 'chambre__type_chambre', 'created_by')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Liste des Réservations'
        context['statuts'] = Reservation.STATUT_CHOICES
        context['search'] = self.request.GET.get('search', '')
        context['today'] = timezone.now().date()
        return context




class ReservationDetailView(LoginRequiredMixin, DetailView):
    model = Reservation
    template_name = 'reservations/reservation_detail.html'
    context_object_name = 'reservation'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Réservation {self.object.numero_reservation}'
        context['is_manager'] = self.request.user.is_staff or self.request.user.is_superuser
        return context


class ReservationCreateView(BaseAjaxCreateView):
    model = Reservation
    form_class = ReservationCreateForm
    template_name = 'reservations/reservation_create.html'
    success_url = reverse_lazy('reservations:list')
    
    def get(self, request, *args, **kwargs):
        """Ouvre le modal → renvoie le formulaire vide"""
        form = self.get_form()
        html = render_to_string(
            self.template_name,
            {'form': form},
            request=request
        )
        return JsonResponse({'html_form': html})

    def post(self, request, *args, **kwargs):
        """Reçoit les données du modal → valide et sauvegarde"""
        print("=== POST ReservationCreateView reçu ===")
        print("Données POST :", request.POST)

        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            print("Formulaire invalide :", form.errors)
            return self.form_invalid(form)

    def form_valid(self, form):
        print("=== FORM_VALID : Réservation en cours de création ===")

        reservation = form.save(commit=False)
        reservation.user_id = self.request.user.id
        reservation.date_reservation = timezone.now()
        reservation.save()  # SAUVEGARDE RÉELLE

        print(f"Réservation #{reservation.id} créée avec succès !")
        print(f"   → Client : {reservation.client}")
        print(f"   → Dates : {reservation.date_arrivee} → {reservation.date_depart}")
        print(f"   → Chambre : {reservation.chambre.numero if reservation.chambre else 'À attribuer'}")

        return JsonResponse({
            'form_is_valid': True,
            'success': True,
            'message': 'Réservation créée !',
            'reservation_id': reservation.id,
        })

    def form_invalid(self, form):
        print("=== FORM_INVALID ===")
        print("Erreurs :", form.errors)

        html = render_to_string(
            self.template_name,
            {'form': form},
            request=self.request
        )
        return JsonResponse({
            'form_is_valid': False,
            'html_form': html,
            'errors': form.errors.get_json_data(),
        })
    

class ReservationUpdateView(BaseAjaxUpdateView):
    model = Reservation
    form_class = ReservationCreateForm
    template_name = 'reservations/reservation_form.html'
    success_url = reverse_lazy('reservations:list')
    
    

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        html = render_to_string(self.template_name, {'form': form}, request=request)
        return JsonResponse({'html_form': html})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        reservation = form.save()
        messages.success(
            self.request,
            f"Réservation {reservation.numero_reservation} modifiée avec succès !"
        )
        return JsonResponse({
            'form_is_valid': True,
            'success': True,
            'message': 'Réservation modifiée avec succès !'
        })

    def form_invalid(self, form):
        html = render_to_string(self.template_name, {'form': form}, request=self.request)
        return JsonResponse({
            'form_is_valid': False,
            'html_form': html
        })


class ReservationDeleteView(DeleteView):
    model = Reservation
    success_url = reverse_lazy('reservations:reservation_list')

    def get(self, request, *args, **kwargs):
        """Charger la confirmation de suppression"""
        self.object = self.get_object()
        
        html_form = render_to_string(
            self.template_name,
            {'employe': self.object}, 
            request=request
        )
        return JsonResponse({'html_form': html_form})

    def post(self, request, *args, **kwargs):
        """Supprimer la reservation"""
        self.object = self.get_object()
        self.object.delete()
        
        data = {
            'form_is_valid': True,
            'success': True,
            'url_redirect': self.success_url
        }
        return JsonResponse(data)





@login_required
def nouvelle_reservation(request):
    if request.method == 'POST':
        form = ReservationCreateForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.cree_par = request.user
            reservation.save()
            return redirect('reservations:calendrier')
    else:
        form = ReservationCreateForm()
    return render(request, 'reservations/nouvelle.html', {'form': form})

@login_required
def calendrier(request):
    return render(request, 'reservations/calendrier.html')

@require_GET
def reservations_calendar_data(request):
    """
    API appelée par FullCalendar
    Paramètres attendus dans GET : start=2025-11-01&end=2025-12-12-01
    """
    start_str = request.GET.get('start')   # ex: "2025-11-01T00:00:00Z"
    end_str = request.GET.get('end')       # ex: "2025-12-13T00:00:00Z"

    # Sécurité si pas de dates (rare mais possible)
    if not start_str or not end_str:
        return JsonResponse([], safe=False)

    # Conversion en date Python
    try:
        start_date = timezone.datetime.fromisoformat(start_str.replace('Z', '+00:00')).date()
        end_date = timezone.datetime.fromisoformat(end_str.replace('Z', '+00:00')).date()
    except:
        return JsonResponse([], safe=False)

    # Récupération uniquement des réservations qui touchent la période
    reservations = Reservation.objects.filter(
        date_arrivee__lte=end_date,
        date_depart__gt=start_date
    ).select_related('client', 'chambre').prefetch_related('chambre__type_chambre')

    events = []

    # Palette de couleurs selon statut
    couleurs = {
        'en_attente': '#ffc107',   # jaune
        'confirmée': '#007bff',    # bleu
        'en_cours': '#28a745',     # vert
        'terminée': '#6c757d',     # gris
        'annulée': '#dc3545',      # rouge
        'no_show': '#343a40',      # noir
    }

    # Remplace toute la boucle for par ça :
    for r in reservations:
     chambre = f"Ch. {r.chambre.numero}" if r.chambre else "À attribuer"
    nom_client = f"{r.client.prenom} {r.client.nom}".strip() if r.client.prenom or r.client.nom else "Client inconnu"
    title = f"{nom_client} – {chambre}"

    events.append({
        "id": r.id,
        "title": title,
        "start": r.date_arrivee.isoformat(),
        "end": (r.date_depart + timedelta(days=1)).isoformat(),
        "url": reverse_lazy('reservations:reservation_detail', args=[r.id]),
        "backgroundColor": couleurs.get(r.statut, '#321fdb'),
        "borderColor": couleurs.get(r.statut, '#321fdb'),
        "textColor": "white",
    })
    return JsonResponse(events, safe=False)

@login_required
def arrivees_du_jour(request):
    aujourd_hui = datetime.today().date()
    arrivees = Reservation.objects.filter(date_arrivee=aujourd_hui, statut__in=['confirmée', 'en_attente'])
    return render(request, 'reservations/arrivées.html', {'arrivees': arrivees})

@login_required
def departs_du_jour(request):
    aujourd_hui = datetime.today().date()
    departs = Reservation.objects.filter(date_depart=aujourd_hui, statut='en_cours')
    return render(request, 'reservations/departs.html', {'departs': departs})

@login_required
def check_in(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, cree_par__hotel=request.user.hotel)

    # Vérifications de sécurité
    if reservation.statut not in ['en_attente', 'confirmée']:
        messages.error(request, f"Impossible : la réservation est déjà {reservation.get_statut_display().lower()}.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('reservations:reservation_list')))

    if reservation.date_arrivee != timezone.localdate():
        messages.warning(request, "Attention : le check-in est fait hors de la date prévue.")
    
    # === ACTION ===
    reservation.statut = 'en_cours'
    reservation.date_checkin = timezone.now()  # ← On enregistre l'heure exacte !
    reservation.save()

    if reservation.chambre:
        reservation.chambre.statut = 'occupee'
        reservation.chambre.save(update_fields=['statut'])

    # Message succès
    messages.success(
        request,
        f"Check-in effectué ! {reservation.client} est maintenant dans la chambre {reservation.chambre}."
    )

    # Redirection intelligente (retour à la page précédente ou défaut)
    redirect_to = request.META.get('HTTP_REFERER')
    if redirect_to and 'check-in' not in redirect_to:
        return HttpResponseRedirect(redirect_to)
    else:
        return redirect('reservations:arrivées')  # ou 'reservations:liste'


@login_required
def check_out(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, cree_par__hotel=request.user.hotel)

    if reservation.statut != 'en_cours':
        messages.error(request, f"Impossible : la réservation n'est pas en cours (statut actuel : {reservation.get_statut_display()})")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('reservations:liste')))

    # === ACTION ===
    reservation.statut = 'terminée'
    reservation.date_checkout = timezone.now()  # ← Heure exacte du départ
    reservation.save()

    if reservation.chambre:
        reservation.chambre.statut = 'sale'  # ou 'a_nettoyer'
        reservation.chambre.save(update_fields=['statut'])

    messages.success(
        request,
        f"Check-out effectué ! La chambre {reservation.chambre} est maintenant à nettoyer."
    )

    # Redirection intelligente
    redirect_to = request.META.get('HTTP_REFERER')
    if redirect_to and 'check-out' not in redirect_to:
        return HttpResponseRedirect(redirect_to)
    else:
        return redirect('reservations:departs')  # ou 'reservations:liste'