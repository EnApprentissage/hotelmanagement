from django.urls import path

from accounts import views
from .views import (
    CongeDeleteView,
    CongeDetailView,
    CongeListView,
    CongeCreateView,
    CongeUpdateView,
    
    EmployeListView,
    EmployeDetailView,
    EmployeCreateView,
    EmployeUpdateView,
    EmployeDeleteView,
    EvaluationCreateView,
    EvaluationDeleteView,
    EvaluationDetailView,
    EvaluationListView,
    EvaluationUpdateView,
    PlanningCreateView,
    PlanningDeleteView,
    PlanningListView,
    PlanningUpdateView,
    PlanningDetailView,
    IncidentListView,
    IncidentDetailView,
    IncidentCreateView,
    IncidentUpdateView,
    IncidentDeleteView,
    employe_documents_upload
)

app_name = 'staff'

urlpatterns = [
    path('employes/', EmployeListView.as_view(), name='employe_list'),
    path('employes/<int:pk>/', EmployeDetailView.as_view(), name='employe_detail'),
    path('employes/add/', EmployeCreateView.as_view(), name='employe_create'),
    path('employes/<int:pk>/edit/', EmployeUpdateView.as_view(), name='employe_update'),
    path('employes/<int:pk>/delete/', EmployeDeleteView.as_view(), name='employe_delete'),
    path('employes/<int:pk>/upload-documents/', employe_documents_upload, name='employe_documents_upload'),
    
    # Planning URLs
    path('planning/', PlanningListView.as_view(), name='planning_list'),
    path('planning/create/', PlanningCreateView.as_view(), name='planning_create'),
    path('planning/<int:pk>/update/', PlanningUpdateView.as_view(), name='planning_update'),
    path('planning/<int:pk>/', PlanningDetailView.as_view(), name='planning_detail'),
    path('planning/<int:pk>/delete/', PlanningDeleteView.as_view(), name='planning_delete'),

    # Congé URLs
    path('conges/', CongeListView.as_view(), name='conge_list'),
    path('conges/<int:pk>/', CongeDetailView.as_view(), name='conge_detail'),
    path('conges/create/', CongeCreateView.as_view(), name='conge_create'),
    path('conges/<int:pk>/update/', CongeUpdateView.as_view(), name='conge_update'),
    path('conges/<int:pk>/delete/', CongeDeleteView.as_view(), name='conge_delete'),

    # Incident URLs
    path('incidents/', IncidentListView.as_view(), name='incident_list'),
    path('incidents/<int:pk>/', IncidentDetailView.as_view(), name='incident_detail'),
    path('incidents/create/', IncidentCreateView.as_view(), name='incident_create'),
    path('incidents/<int:pk>/update/', IncidentUpdateView.as_view(), name='incident_update'),
    path('incidents/<int:pk>/delete/', IncidentDeleteView.as_view(), name='incident_delete'),

    # Évaluations
    path('evaluations/', EvaluationListView.as_view(), name='evaluation_list'),
    path('evaluations/<int:pk>/', EvaluationDetailView.as_view(), name='evaluation_detail'),
    path('evaluations/create/', EvaluationCreateView.as_view(), name='evaluation_create'),
    path('evaluations/<int:pk>/update/', EvaluationUpdateView.as_view(), name='evaluation_update'),
    path('evaluations/<int:pk>/delete/', EvaluationDeleteView.as_view(), name='evaluation_delete'),
]
