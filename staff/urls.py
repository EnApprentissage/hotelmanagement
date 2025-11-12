from django.urls import path
from .views import (
    CongeDeleteView,
    CongeListView,
    CongeCreateView,
    CongeUpdateView,
    
    EmployeListView,
    EmployeDetailView,
    EmployeCreateView,
    EmployeUpdateView,
    EmployeDeleteView,
    PlanningCreateView,
    PlanningDeleteView,
    PlanningListView,
    PlanningUpdateView,
)

app_name = 'staff'

urlpatterns = [
    path('employes/', EmployeListView.as_view(), name='employe_list'),
    path('employes/<int:pk>/', EmployeDetailView.as_view(), name='employe_detail'),
    path('employes/add/', EmployeCreateView.as_view(), name='employe_create'),
    path('employes/<int:pk>/edit/', EmployeUpdateView.as_view(), name='employe_update'),
    path('employes/<int:pk>/delete/', EmployeDeleteView.as_view(), name='employe_delete'),

    # Planning URLs
    path('planning/', PlanningListView.as_view(), name='planning_list'),
    path('planning/create/', PlanningCreateView.as_view(), name='planning_create'),
    path('planning/<int:pk>/update/', PlanningUpdateView.as_view(), name='planning_update'),
    path('planning/<int:pk>/delete/', PlanningDeleteView.as_view(), name='planning_delete'),

    # Congé URLs
    path('conges/', CongeListView.as_view(), name='conge_list'),
    path('conges/add/', CongeCreateView.as_view(), name='conge_create'),
    path('conges/<int:pk>/edit/', CongeUpdateView.as_view(), name='conge_update'),
    path('conges/<int:pk>/delete/', CongeDeleteView.as_view(), name='conge_delete'),
]
