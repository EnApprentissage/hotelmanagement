# chambres/urls.py
from django.urls import path
from . import views

app_name = 'chambres'

urlpatterns = [
    # Liste et CRUD
    path('chambres/', views.ChambreListView.as_view(), name='chambre_list'),
    path('chambres/<int:pk>/', views.ChambreDetailView.as_view(), name='chambre_detail'),
    path('chambres/create/', views.ChambreCreateView.as_view(), name='chambre_create'),
    path('chambres/<int:pk>/edit/', views.ChambreUpdateView.as_view(), name='chambre_update'),
    path('chambres/<int:pk>/delete/', views.ChambreDeleteView.as_view(), name='chambre_delete'),
    
    # NOUVEAU : Mise à jour du statut (pour nettoyage)
    path('chambres/<int:pk>/update-status/', views.update_chambre_status, name='chambre_update_status'),
    
    # NOUVEAU : Vue spéciale pour le personnel de ménage
    path('chambres/nettoyage/', views.chambres_a_nettoyer, name='chambres_nettoyage'),

    # Maintenance
    path('maintenances/', views.maintenance_list, name='maintenance_list'),
    path('maintenances/<int:pk>/', views.maintenance_detail, name='maintenance_detail'),
]