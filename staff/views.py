# staff/views.py
from pyexpat.errors import messages
from urllib import request
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q

from hotel_management_system.base_views import BaseAjaxCreateView, BaseAjaxDeleteView, BaseAjaxDeleteView, BaseAjaxUpdateView
from django.utils.translation import gettext_lazy as _
from .models import Employe, Planning, Pointage, Conge, Evaluation, Incident
from .forms import (
    EmployeForm, PlanningForm, PointageForm,
    CongeForm, EvaluationForm, IncidentForm
)
from .template import   StaffTemplate


# ==================== EMPLOYE ====================
class EmployeListView(ListView):
    model = Employe
    template_name = 'staff/employe_list.html'
    context_object_name = 'employes'
    paginate_by = 10  # ← nombre d’employés par page
    ordering = ['nom']

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        departement = self.request.GET.get('departement')

        if search:
            queryset = queryset.filter(
                Q(nom__icontains=search) |
                Q(prenom__icontains=search) | # pyright: ignore[reportUndefinedVariable]
                Q(matricule__icontains=search) |
                Q(poste__icontains=search)
            )
        if departement and departement != "":
            queryset = queryset.filter(departement__icontains=departement)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departements'] = Employe.objects.values_list('departement', flat=True).distinct()
        context['search'] = self.request.GET.get('search', '')
        context['selected_departement'] = self.request.GET.get('departement', '')
        return context

class EmployeDetailView(DetailView):
    model = Employe
    template_name = 'staff/employe_detail.html'


class EmployeCreateView(BaseAjaxCreateView):
    model = Employe
    form_class = EmployeForm
    template_name = StaffTemplate.create_template
    success_url = reverse_lazy('staff:employe_list')
    success_message = _('Employé créé avec succès')

    def get(self, request, *args, **kwargs):
        """Charger le formulaire vide dans la modale"""
        self.object = None
        form = self.get_form()
        
        # Rendre le template modal complet
        html_form = render_to_string(
            self.template_name,
            {'form': form}, 
            request=request
        )
        
        print("=== DEBUG GET CREATE ===")
        print(f"Template: {self.template_name}")
        print(f"HTML Form length: {len(html_form)}")
        
        return JsonResponse({'html_form': html_form})

    def post(self, request, *args, **kwargs):
        """Traiter la soumission du formulaire"""
        self.object = None
        form = self.get_form()
        
        print("=== DEBUG POST CREATE ===")
        print(f"Form data: {request.POST}")
        print(f"Form is valid: {form.is_valid()}")
        
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """Sauvegarder et retourner le contenu mis à jour"""
        try:
            # Sauvegarder sans commit pour ajouter l'utilisateur
            instance = form.save(commit=False)
            
            # Assigner l'utilisateur connecté (utiliser user_id pour éviter les problèmes)
            instance.user_id = self.request.user.id
            
            instance.save()
            
            print(f"=== Employé créé avec succès: {instance.nom} {instance.prenom} ===")
            
            # Retourner une réponse JSON pour recharger la page
            data = {
                'form_is_valid': True,
                'url_redirect': self.success_url  # Rediriger vers la liste
            }
            
            return JsonResponse(data)
            
            data = {
                'form_is_valid': True,
                'url_redirect': self.success_url  # Rediriger vers la liste
            }
            
            return JsonResponse(data)
            
        except Exception as e:
            print(f"=== ERREUR lors de la sauvegarde: {str(e)} ===")
            import traceback
            traceback.print_exc()
            
            return JsonResponse({
                'form_is_valid': False,
                'html_form': render_to_string(
                    self.template_name,
                    {'form': form, 'error': str(e)}, 
                    request=self.request
                )
            })

    def form_invalid(self, form):
        """Retourner le formulaire avec les erreurs"""
        print(f"=== FORM INVALID - Errors: {form.errors} ===")
        
        html_form = render_to_string(
            self.template_name,
            {'form': form}, 
            request=self.request
        )
        
        return JsonResponse({
            'form_is_valid': False,
            'html_form': html_form
        })

class EmployeUpdateView(BaseAjaxUpdateView):
    model = Employe
    form_class = EmployeForm
    template_name = StaffTemplate.update_template
    success_url = reverse_lazy('staff:employe_list')
    success_message = _('Employé mis à jour avec succès')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            self.object = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'form_is_valid': True,
                    'url_redirect': str(self.success_url),
                    'message': self.success_message
                })
            return redirect(self.success_url)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html_form = render_to_string(
                    self.template_name,
                    {'form': form, 'object': self.object},
                    request=request
                )
                return JsonResponse({'form_is_valid': False, 'html_form': html_form})
            return self.form_invalid(form)



class EmployeDeleteView(DeleteView):
    model = Employe
    success_url = reverse_lazy('staff:employe_list')

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
        """Supprimer l'employé"""
        self.object = self.get_object()
        self.object.delete()
        
        data = {
            'form_is_valid': True,
            'success': True,
            'url_redirect': self.success_url
        }
        return JsonResponse(data)


# ==================== PLANNING ====================
class PlanningListView(ListView):
    model = Planning
    template_name = 'staff/planning_list.html'
    context_object_name = 'plannings'
    ordering = ['-date']
    paginate_by = 10  # ✅ 10 plannings par page

    def get_queryset(self):
        queryset = super().get_queryset()
        date_debut = self.request.GET.get('date_debut')
        date_fin = self.request.GET.get('date_fin')
        employe_id = self.request.GET.get('employe')

        # ✅ Filtrage dynamique
        if date_debut:
            queryset = queryset.filter(date__gte=date_debut)
        if date_fin:
            queryset = queryset.filter(date__lte=date_fin)
        if employe_id:
            queryset = queryset.filter(employe_id=employe_id)

        return queryset.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employes'] = Employe.objects.all().order_by('prenom')
        context['is_paginated'] = self.paginate_by is not None
        return context



class PlanningCreateView(BaseAjaxCreateView):
    model = Planning
    form_class = PlanningForm
    template_name = 'staff/planning_form.html'
    success_url = reverse_lazy('staff:planning_list')
    success_message = _('Planning créé avec succès')

    def get(self, request, *args, **kwargs):
        """Charger le formulaire vide dans la modale"""
        self.object = None
        form = self.get_form()
        
        html_form = render_to_string(
            self.template_name,
            {'form': form}, 
            request=request
        )
        
        return JsonResponse({'html_form': html_form})

    def post(self, request, *args, **kwargs):
        """Traiter la soumission du formulaire"""
        self.object = None
        form = self.get_form()
        
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """Sauvegarder et rediriger"""
        try:
            instance = form.save(commit=False)
            instance.user_id = self.request.user.id
            instance.save()

            # Message de succès (optionnel, si tu utilises messages)
            if self.success_message:
                messages.success(self.request, self.success_message)

            return JsonResponse({
                'form_is_valid': True,
                'url_redirect': self.success_url  # Redirige vers la liste
            })

        except Exception as e:
            return JsonResponse({
                'form_is_valid': False,
                'html_form': render_to_string(
                    self.template_name,
                    {'form': form, 'error': str(e)}, 
                    request=self.request
                )
            })

    def form_invalid(self, form):
        """Retourner le formulaire avec erreurs"""
        html_form = render_to_string(
            self.template_name,
            {'form': form}, 
            request=self.request
        )
        return JsonResponse({
            'form_is_valid': False,
            'html_form': html_form
        })

class PlanningUpdateView(BaseAjaxUpdateView):
    model = Planning
    form_class = PlanningForm
    template_name = 'staff/planning_form.html'
    success_url = reverse_lazy('staff:planning_list')
    success_message = _('Planning mis à jour avec succès')

    def get_object(self):
        return get_object_or_404(Planning, pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        html_form = render_to_string(
            self.template_name,
            {'form': form},
            request=request
        )
        return JsonResponse({'html_form': html_form})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        try:
            instance = form.save(commit=False)
            instance.save()  # user déjà assigné à la création
            if self.success_message:
                messages.success(self.request, self.success_message)

            return JsonResponse({
                'form_is_valid': True,
                'url_redirect': self.success_url
            })
        except Exception as e:
            return JsonResponse({
                'form_is_valid': False,
                'html_form': render_to_string(
                    self.template_name,
                    {'form': form, 'error': str(e)},
                    request=self.request
                )
            })

    def form_invalid(self, form):
        html_form = render_to_string(
            self.template_name,
            {'form': form},
            request=self.request
        )
        return JsonResponse({
            'form_is_valid': False,
            'html_form': html_form
        })

    

class PlanningDeleteView(DeleteView):
    model = Planning
    template_name = 'staff/planning_confirm_delete.html'
    success_url = reverse_lazy('staff:planning_list')

    def get(self, request, *args, **kwargs):
        """Charger la confirmation de suppression"""
        self.object = self.get_object()
        
        html_form = render_to_string(
            self.template_name,
            {'planning': self.object}, 
            request=request
        )
        return JsonResponse({'html_form': html_form})

    def post(self, request, *args, **kwargs):
        """Supprimer le planning"""
        self.object = self.get_object()
        self.object.delete()
        
        data = {
            'form_is_valid': True,
            'success': True,
            'url_redirect': self.success_url
        }
        return JsonResponse(data)



    
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
    paginate_by = 10

    def get_queryset(self):
        qs = Conge.objects.select_related('employe').all()
        employe = self.request.GET.get('employe')
        date_debut = self.request.GET.get('date_debut')
        date_fin = self.request.GET.get('date_fin')

        if employe:
            qs = qs.filter(employe_id=employe)
        if date_debut:
            qs = qs.filter(date_debut__gte=date_debut)
        if date_fin:
            qs = qs.filter(date_fin__lte=date_fin)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employes'] = Employe.objects.all()
        return context


class CongeCreateView(BaseAjaxCreateView):
    model = Conge
    form_class = CongeForm
    template_name = 'staff/conge_form.html'
    success_url = reverse_lazy('staff:conge_list')

    def get(self, request, *args, **kwargs):
        """Charge le formulaire vide dans la modale"""
        form = self.get_form()
        html_form = render_to_string(self.template_name, {'form': form}, request=request)
        return JsonResponse({'html_form': html_form})

    def post(self, request, *args, **kwargs):
        """Traite la soumission AJAX"""
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.save()
        data = {
            'form_is_valid': True,
            'success_message': self.success_message,
        }
        return JsonResponse(data)

    def form_invalid(self, form):
        html_form = render_to_string(self.template_name, {'form': form}, request=self.request)
        return JsonResponse({'form_is_valid': False, 'html_form': html_form})



class CongeUpdateView(UpdateView):
    model = Conge
    form_class = CongeForm
    template_name = 'staff/conge_form.html'
    success_url = reverse_lazy('staff:conge_list')

    def get(self, request, *args, **kwargs):
        """Charge le formulaire vide dans la modale"""
        form = self.get_form()
        html_form = render_to_string(self.template_name, {'form': form}, request=request)
        return JsonResponse({'html_form': html_form})

    def post(self, request, *args, **kwargs):
        """Traite la soumission AJAX"""
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.save()
        data = {
            'form_is_valid': True,
            'success_message': self.success_message,
        }
        return JsonResponse(data)

    def form_invalid(self, form):
        html_form = render_to_string(self.template_name, {'form': form}, request=self.request)
        return JsonResponse({'form_is_valid': False, 'html_form': html_form})
    
class CongeDeleteView(DeleteView):
    model = Conge
    success_url = reverse_lazy('staff:conge_list')

    def post(self, request, *args, **kwargs):
        conge = self.get_object()
        conge.delete()
        return JsonResponse({'success': True})


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