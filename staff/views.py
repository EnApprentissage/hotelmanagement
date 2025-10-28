# staff/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Employe, Planning, Pointage, Conge, Evaluation, Incident
from .forms import (
    EmployeForm, PlanningForm, PointageForm,
    CongeForm, EvaluationForm, IncidentForm
)


# ==================== EMPLOYE ====================
class EmployeListView(ListView):
    model = Employe
    template_name = 'staff/employe_list.html'
    context_object_name = 'employes'
    ordering = ['nom']


class EmployeDetailView(DetailView):
    model = Employe
    template_name = 'staff/employe_detail.html'


class EmployeCreateView(CreateView):
    model = Employe
    form_class = EmployeForm
    template_name = 'staff/employe_form.html'
    success_url = reverse_lazy('staff:employe_list')


class EmployeUpdateView(UpdateView):
    model = Employe
    form_class = EmployeForm
    template_name = 'staff/employe_form.html'
    success_url = reverse_lazy('staff:employe_list')


class EmployeDeleteView(DeleteView):
    model = Employe
    template_name = 'staff/employe_confirm_delete.html'
    success_url = reverse_lazy('staff:employe_list')


# ==================== PLANNING ====================
class PlanningListView(ListView):
    model = Planning
    template_name = 'staff/planning_list.html'
    context_object_name = 'plannings'
    ordering = ['-date']


class PlanningCreateView(CreateView):
    model = Planning
    form_class = PlanningForm
    template_name = 'staff/planning_form.html'
    success_url = reverse_lazy('staff:planning_list')


class PlanningUpdateView(UpdateView):
    model = Planning
    form_class = PlanningForm
    template_name = 'staff/planning_form.html'
    success_url = reverse_lazy('staff:planning_list')


class PlanningDeleteView(DeleteView):
    model = Planning
    template_name = 'staff/planning_confirm_delete.html'
    success_url = reverse_lazy('staff:planning_list')


# ==================== POINTAGE ====================
class PointageListView(ListView):
    model = Pointage
    template_name = 'staff/pointage_list.html'
    context_object_name = 'pointages'
    ordering = ['-date']


class PointageCreateView(CreateView):
    model = Pointage
    form_class = PointageForm
    template_name = 'staff/pointage_form.html'
    success_url = reverse_lazy('staff:pointage_list')


class PointageUpdateView(UpdateView):
    model = Pointage
    form_class = PointageForm
    template_name = 'staff/pointage_form.html'
    success_url = reverse_lazy('staff:pointage_list')


# ==================== CONGE ====================
class CongeListView(ListView):
    model = Conge
    template_name = 'staff/conge_list.html'
    context_object_name = 'conges'
    ordering = ['-date_demande']


class CongeCreateView(CreateView):
    model = Conge
    form_class = CongeForm
    template_name = 'staff/conge_form.html'
    success_url = reverse_lazy('staff:conge_list')


class CongeUpdateView(UpdateView):
    model = Conge
    form_class = CongeForm
    template_name = 'staff/conge_form.html'
    success_url = reverse_lazy('staff:conge_list')


# ==================== EVALUATION ====================
class EvaluationListView(ListView):
    model = Evaluation
    template_name = 'staff/evaluation_list.html'
    context_object_name = 'evaluations'
    ordering = ['-date_evaluation']


class EvaluationCreateView(CreateView):
    model = Evaluation
    form_class = EvaluationForm
    template_name = 'staff/evaluation_form.html'
    success_url = reverse_lazy('staff:evaluation_list')


class EvaluationUpdateView(UpdateView):
    model = Evaluation
    form_class = EvaluationForm
    template_name = 'staff/evaluation_form.html'
    success_url = reverse_lazy('staff:evaluation_list')


# ==================== INCIDENT ====================
class IncidentListView(ListView):
    model = Incident
    template_name = 'staff/incident_list.html'
    context_object_name = 'incidents'
    ordering = ['-date_incident']


class IncidentCreateView(CreateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'staff/incident_form.html'
    success_url = reverse_lazy('staff:incident_list')


class IncidentUpdateView(UpdateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'staff/incident_form.html'
    success_url = reverse_lazy('staff:incident_list')