# reservations/urls.py

from django.urls import path

# On importe TOUT importer depuis l'app reservations (pas depuis accounts !)
from .views import (
    ReservationListView,
    ReservationDetailView,
    ReservationCreateView,
    ReservationUpdateView,
    ReservationDeleteView,
    calendrier,                       # ← ta vue qui affiche le calendrier
    reservations_calendar_data,       # ← l'API FullCalendar
    arrivees_du_jour,
    departs_du_jour,
    check_in,
    check_out,
)

app_name = 'reservations'

urlpatterns = [
    # Liste / CRUD classique
    path('', ReservationListView.as_view(), name='reservation_list'),                    # → /reservations/
    path('<int:pk>/', ReservationDetailView.as_view(), name='reservation_detail'),
    path('create/', ReservationCreateView.as_view(), name='reservation_create'),
    path('<int:pk>/update/', ReservationUpdateView.as_view(), name='reservation_update'),
    path('<int:pk>/delete/', ReservationDeleteView.as_view(), name='reservation_delete'),

    # Pages fonctionnelles
    path('reservations/', calendrier, name='calendrier'),                                 # → /reservations/calendrier/
    path('arrivees/', arrivees_du_jour, name='arrivees'),
    path('departs/', departs_du_jour, name='departs'),

    # Actions rapides
    path('check-in/<int:pk>/', check_in, name='check_in'),
    path('check-out/<int:pk>/', check_out, name='check_out'),

    # API FullCalendar (très important : pas de "reservations/" devant ici)
    path('api/calendar/', reservations_calendar_data, name='calendar_data'),
]