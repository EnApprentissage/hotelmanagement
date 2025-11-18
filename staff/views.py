# staff/views.py
from datetime import date
from pyexpat.errors import messages
from urllib import request
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views import View
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
    context_object_name = 'employe'

    def get_object(self):
        """Récupérer l'employé"""
        return get_object_or_404(Employe, pk=self.kwargs['pk'])

    def calculate_age(self, birth_date):
        """Calculer l'âge à partir de la date de naissance"""
        if not birth_date:
            return None
        
        today = date.today()
        age = today.year - birth_date.year
        
        # Vérifier si l'anniversaire n'est pas encore passé cette année
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1
        
        return age

    def calculate_anciennete(self, date_embauche):
        """Calculer l'ancienneté en années"""
        if not date_embauche:
            return None
        
        today = date.today()
        years = today.year - date_embauche.year
        
        # Ajuster si l'anniversaire d'embauche n'est pas encore passé
        if today.month < date_embauche.month or (today.month == date_embauche.month and today.day < date_embauche.day):
            years -= 1
        
        return years

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employe = self.object
        
        # Calculer l'âge
        if employe.date_naissance:
            context['age'] = self.calculate_age(employe.date_naissance)
        else:
            context['age'] = None
        
        # Calculer l'ancienneté en années
        if employe.date_embauche:
            context['anciennete_annees'] = self.calculate_anciennete(employe.date_embauche)
        else:
            context['anciennete_annees'] = None
        
        # Compter les congés de l'employé
        context['conges_count'] = Conge.objects.filter(employe=employe).count()
        
        # Compter les plannings de l'employé
        context['plannings_count'] = Planning.objects.filter(employe=employe).count()
        
        # Récupérer les 5 derniers congés
        context['recent_conges'] = (
            Conge.objects
            .filter(employe=employe)
            .order_by('-date_debut')[:5]
        )
        
        # Récupérer les 5 derniers plannings
        context['recent_plannings'] = (
            Planning.objects
            .filter(employe=employe)
            .order_by('-date')[:5]
        )
        
        return context

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
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('employe')
        
        # 🔍 Récupération des paramètres de filtrage
        nom = self.request.GET.get('nom', '').strip()
        prenom = self.request.GET.get('prenom', '').strip()
        matricule = self.request.GET.get('matricule', '').strip()
        departement = self.request.GET.get('departement', '').strip()
        periode = self.request.GET.get('periode', '').strip()

        # ✅ Filtrage par nom de l'employé
        if nom:
            queryset = queryset.filter(employe__nom__icontains=nom)
        
        # ✅ Filtrage par prénom de l'employé
        if prenom:
            queryset = queryset.filter(employe__prenom__icontains=prenom)
        
        # ✅ Filtrage par matricule de l'employé
        if matricule:
            queryset = queryset.filter(employe__matricule__icontains=matricule)
        
        # ✅ Filtrage par département de l'employé
        if departement:
            queryset = queryset.filter(employe__departement=departement)
        
        # ✅ Filtrage par période
        if periode:
            queryset = queryset.filter(periode=periode)

        return queryset.order_by('-date', 'employe__nom')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 📋 Liste des départements uniques
        context['departements'] = (
            Employe.objects.exclude(departement__isnull=True)
            .exclude(departement='')
            .values_list('departement', flat=True)
            .distinct()
            .order_by('departement')
        )
        
        # ✅ Indiquer qu'on utilise la pagination
        context['is_paginated'] = self.paginate_by is not None
        
        return context
    

class PlanningDetailView(DetailView):
    model = Planning
    template_name = 'staff/planning_detail.html'
    context_object_name = 'planning'


    
class PlanningCreateView(BaseAjaxCreateView):
    model = Planning
    form_class = PlanningForm
    template_name = 'staff/planning_form.html'
    success_url = reverse_lazy('staff:planning_list')
    success_message = _('Planning créé avec succès')

    def get(self, request, *args, **kwargs):
        """Charger le formulaire vide dans la modale"""
        print("=== GET PlanningCreateView ===")
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
        print("=== POST PlanningCreateView ===")
        print("POST data:", request.POST)
        
        self.object = None
        form = self.get_form()
        
        print("Form errors:", form.errors if not form.is_valid() else "Aucune erreur")
        
        if form.is_valid():
            print("✅ Formulaire valide")
            return self.form_valid(form)
        else:
            print("❌ Formulaire invalide")
            return self.form_invalid(form)

    def form_valid(self, form):
        """Sauvegarder et rediriger"""
        try:
            print("=== form_valid (CREATE) ===")
            instance = form.save(commit=False)
            
            # ✅ Assigner l'utilisateur si nécessaire
            if hasattr(instance, 'user_id') and not instance.user_id:
                instance.user_id = self.request.user.id
                print(f"User assigné: {instance.user_id}")
            
            instance.save()
            print(f"✅ Planning créé: ID={instance.pk}, Date={instance.date}, Employé={instance.employe}")

            # ✅ Message de succès
            if self.success_message:
                messages.success(self.request, self.success_message)

            return JsonResponse({
                'form_is_valid': True
            })

        except Exception as e:
            print(f"❌ ERREUR dans form_valid: {str(e)}")
            import traceback
            traceback.print_exc()
            form.add_error(None, f"Erreur lors de la création : {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Retourner le formulaire avec erreurs"""
        print("=== form_invalid (CREATE) ===")
        print("Erreurs du formulaire:", form.errors)
        print("Erreurs non-field:", form.non_field_errors())
        
        html_form = render_to_string(
            self.template_name,
            {'form': form}, 
            request=self.request
        )
        
        return JsonResponse({
       'form_is_valid': True,
       'success': True  # ✅ Ajouté
   })

    
class PlanningUpdateView(BaseAjaxUpdateView):
    model = Planning
    form_class = PlanningForm
    template_name = 'staff/planning_form.html'
    success_url = reverse_lazy('staff:planning_list')
    success_message = _('Planning mis à jour avec succès')

    def get_object(self):
        """Récupérer l'objet Planning"""
        return get_object_or_404(Planning, pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        """Charger le formulaire pré-rempli dans la modale"""
        print(f"=== GET PlanningUpdateView (PK={self.kwargs['pk']}) ===")
        self.object = self.get_object()
        form = self.get_form()
        
        html_form = render_to_string(
            self.template_name,
            {'form': form, 'object': self.object},
            request=request
        )
        
        return JsonResponse({'html_form': html_form})

    def post(self, request, *args, **kwargs):
        """Traiter la soumission du formulaire de modification"""
        print(f"=== POST PlanningUpdateView (PK={self.kwargs['pk']}) ===")
        print("POST data:", request.POST)
        
        self.object = self.get_object()
        form = self.get_form()
        
        print("Form errors:", form.errors if not form.is_valid() else "Aucune erreur")
        
        if form.is_valid():
            print("✅ Formulaire valide")
            return self.form_valid(form)
        else:
            print("❌ Formulaire invalide")
            return self.form_invalid(form)

    def form_valid(self, form):
        """Sauvegarder les modifications"""
        try:
            print("=== form_valid (UPDATE) ===")
            instance = form.save(commit=False)
            instance.save()
            
            print(f"✅ Planning modifié: ID={instance.pk}, Date={instance.date}, Employé={instance.employe}")
            
            # ✅ Message de succès
            if self.success_message:
                messages.success(self.request, self.success_message)

            return JsonResponse({
                'form_is_valid': True
            })
            
        except Exception as e:
            print(f"❌ ERREUR dans form_valid: {str(e)}")
            import traceback
            traceback.print_exc()
            form.add_error(None, f"Erreur lors de la modification : {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Retourner le formulaire avec erreurs"""
        print("=== form_invalid (UPDATE) ===")
        print("Erreurs du formulaire:", form.errors)
        print("Erreurs non-field:", form.non_field_errors())
        
        html_form = render_to_string(
            self.template_name,
            {'form': form, 'object': self.object},
            request=self.request
        )
        return JsonResponse({
       'form_is_valid': True,
       'success': True  # ✅ Ajouté
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
    ordering = ['-date_debut']
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('employe')
        
        # Récupération du paramètre de recherche unifié
        search = self.request.GET.get('search', '').strip()
        type_conge = self.request.GET.get('type_conge', '').strip()
        statut = self.request.GET.get('statut', '').strip()

        # Recherche unifiée sur plusieurs champs
        if search:
            queryset = queryset.filter(
                Q(employe__nom__icontains=search) |
                Q(employe__prenom__icontains=search) |
                Q(employe__matricule__icontains=search) |
                Q(employe__poste__icontains=search)
            )
        
        # Filtrage par type de congé
        if type_conge:
            queryset = queryset.filter(type_conge=type_conge)
        
        # Filtrage par statut
        if statut:
            queryset = queryset.filter(statut=statut)

        return queryset.order_by('-date_debut', 'employe__nom')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Passer le terme de recherche au template
        context['search'] = self.request.GET.get('search', '')
        
        # Récupérer les choices depuis le champ du modèle
        type_conge_field = Conge._meta.get_field('type_conge')
        context['type_choices'] = type_conge_field.choices

        statut_field = Conge._meta.get_field('statut')
        context['statut_choices'] = statut_field.choices

        # Indiquer qu'on utilise la pagination
        context['is_paginated'] = self.paginate_by is not None
        
        return context


class CongeDetailView(DetailView):
    model = Conge
    template_name = 'staff/conge_detail.html'
    context_object_name = 'conge'


class CongeCreateView(BaseAjaxCreateView):
    model = Conge
    form_class = CongeForm
    template_name = 'staff/conge_create.html'  # ✅ IMPORTANT: Utiliser conge_create.html
    success_url = reverse_lazy('staff:conge_list')
    success_message = _('Congé créé avec succès')

    def get(self, request, *args, **kwargs):
        """Charger le formulaire vide dans la modale"""
        print("=== GET CongeCreateView ===")
        print(f"Template utilisé: {self.template_name}")  # Debug
        
        self.object = None
        form = self.get_form()
        
        # ✅ IMPORTANT: Utiliser le bon template avec les boutons
        html_form = render_to_string(
            self.template_name,  # conge_create.html
            {'form': form}, 
            request=request
        )
        
        return JsonResponse({'html_form': html_form})

    def post(self, request, *args, **kwargs):
        """Traiter la soumission du formulaire"""
        print("=== POST CongeCreateView ===")
        print("POST data:", request.POST)
        
        self.object = None
        form = self.get_form()
        
        print("Form errors:", form.errors if not form.is_valid() else "Aucune erreur")
        
        if form.is_valid():
            print("✅ Formulaire valide")
            return self.form_valid(form)
        else:
            print("❌ Formulaire invalide")
            return self.form_invalid(form)

    def form_valid(self, form):
        """Sauvegarder et rediriger"""
        try:
            print("=== form_valid (CREATE) ===")
            instance = form.save(commit=False)
            
            # Assigner l'utilisateur si nécessaire
            if hasattr(instance, 'user_id') and not instance.user_id:
                instance.user_id = self.request.user.id
                print(f"User assigné: {instance.user_id}")
            
            instance.save()
            print(f"✅ Congé créé: ID={instance.pk}, Employé={instance.employe}, Dates={instance.date_debut} → {instance.date_fin}")

            # Message de succès
            if self.success_message:
                messages.success(self.request, self.success_message)

            return JsonResponse({
                'form_is_valid': True,
                'success': True
            })

        except Exception as e:
            print(f"❌ ERREUR dans form_valid: {str(e)}")
            import traceback
            traceback.print_exc()
            form.add_error(None, f"Erreur lors de la création : {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Retourner le formulaire avec erreurs"""
        print("=== form_invalid (CREATE) ===")
        print("Erreurs du formulaire:", form.errors)
        print("Erreurs non-field:", form.non_field_errors())
        
        # ✅ IMPORTANT: Utiliser le bon template même en cas d'erreur
        html_form = render_to_string(
            self.template_name,  # conge_create.html
            {'form': form}, 
            request=self.request
        )
        
        return JsonResponse({
        'form_is_valid': True,  # ❌ FAUX !
        'success': True  # ❌ FAUX !
    })


class CongeUpdateView(BaseAjaxUpdateView):
    model = Conge
    form_class = CongeForm
    template_name = 'staff/conge_update.html'  # ✅ IMPORTANT: Utiliser conge_update.html
    success_url = reverse_lazy('staff:conge_list')
    success_message = _('Congé mis à jour avec succès')

    def get_object(self):
        """Récupérer l'objet Conge"""
        return get_object_or_404(Conge, pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        """Charger le formulaire pré-rempli dans la modale"""
        print(f"=== GET CongeUpdateView (PK={self.kwargs['pk']}) ===")
        print(f"Template utilisé: {self.template_name}")  # Debug
        
        self.object = self.get_object()
        form = self.get_form()
        
        # ✅ IMPORTANT: Utiliser le bon template avec les boutons
        html_form = render_to_string(
            self.template_name,  # conge_update.html
            {'form': form, 'object': self.object},
            request=request
        )
        
        return JsonResponse({'html_form': html_form})

    def post(self, request, *args, **kwargs):
        """Traiter la soumission du formulaire de modification"""
        print(f"=== POST CongeUpdateView (PK={self.kwargs['pk']}) ===")
        print("POST data:", request.POST)
        
        self.object = self.get_object()
        form = self.get_form()
        
        print("Form errors:", form.errors if not form.is_valid() else "Aucune erreur")
        
        if form.is_valid():
            print("✅ Formulaire valide")
            return self.form_valid(form)
        else:
            print("❌ Formulaire invalide")
            return self.form_invalid(form)

    def form_valid(self, form):
        """Sauvegarder les modifications"""
        try:
            print("=== form_valid (UPDATE) ===")
            instance = form.save(commit=False)
            instance.save()
            
            print(f"✅ Congé modifié: ID={instance.pk}, Employé={instance.employe}, Dates={instance.date_debut} → {instance.date_fin}")
            
            # Message de succès
            if self.success_message:
                messages.success(self.request, self.success_message)

            return JsonResponse({
                'form_is_valid': True,
                'success': True
            })
            
        except Exception as e:
            print(f"❌ ERREUR dans form_valid: {str(e)}")
            import traceback
            traceback.print_exc()
            form.add_error(None, f"Erreur lors de la modification : {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Retourner le formulaire avec erreurs"""
        print("=== form_invalid (UPDATE) ===")
        print("Erreurs du formulaire:", form.errors)
        print("Erreurs non-field:", form.non_field_errors())
        
        # ✅ IMPORTANT: Utiliser le bon template même en cas d'erreur
        html_form = render_to_string(
            self.template_name,  # conge_update.html
            {'form': form, 'object': self.object},
            request=self.request
        )
        
        return JsonResponse({
        'form_is_valid': True,  # ❌ FAUX !
        'success': True  # ❌ FAUX !
    })
    
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
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('employe', 'signale_par')
        
        # Récupération du paramètre de recherche unifié
        search = self.request.GET.get('search', '').strip()
        type_incident = self.request.GET.get('type_incident', '').strip()
        sanction = self.request.GET.get('sanction', '').strip()

        # Recherche unifiée sur plusieurs champs
        if search:
            queryset = queryset.filter(
                Q(employe__nom__icontains=search) |
                Q(employe__prenom__icontains=search) |
                Q(employe__matricule__icontains=search) |
                Q(employe__poste__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Filtrage par type d'incident
        if type_incident:
            queryset = queryset.filter(type_incident=type_incident)
        
        # Filtrage par sanction
        if sanction:
            queryset = queryset.filter(sanction=sanction)

        return queryset.order_by('-date_incident', 'employe__nom')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Passer le terme de recherche au template
        context['search'] = self.request.GET.get('search', '')
        
        # Récupérer les choices depuis le champ du modèle
        type_incident_field = Incident._meta.get_field('type_incident')
        context['type_choices'] = type_incident_field.choices

        sanction_field = Incident._meta.get_field('sanction')
        context['sanction_choices'] = sanction_field.choices

        # Indiquer qu'on utilise la pagination
        context['is_paginated'] = self.paginate_by is not None
        
        return context


class IncidentDetailView(DetailView):
    model = Incident
    template_name = 'staff/incident_detail.html'
    context_object_name = 'incident'


class IncidentCreateView(BaseAjaxCreateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'staff/incident_create.html'
    success_url = reverse_lazy('staff:incident_list')
    success_message = _('Incident enregistré avec succès')

    def get(self, request, *args, **kwargs):
        """Charger le formulaire vide dans la modale"""
        print("=== GET IncidentCreateView ===")
        print(f"Template utilisé: {self.template_name}")
        
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
        print("=== POST IncidentCreateView ===")
        print("POST data:", request.POST)
        
        self.object = None
        form = self.get_form()
        
        print("Form errors:", form.errors if not form.is_valid() else "Aucune erreur")
        
        if form.is_valid():
            print("✅ Formulaire valide")
            return self.form_valid(form)
        else:
            print("❌ Formulaire invalide")
            return self.form_invalid(form)

    def form_valid(self, form):
        """Sauvegarder et rediriger"""
        try:
            print("=== form_valid (CREATE) ===")
            instance = form.save(commit=False)
            
            # Assigner l'utilisateur qui signale
            instance.signale_par = self.request.user
            print(f"Signalé par: {instance.signale_par}")
            
            instance.save()
            print(f"✅ Incident créé: ID={instance.pk}, Employé={instance.employe}, Type={instance.type_incident}")

            # Message de succès
            if self.success_message:
                messages.success(self.request, self.success_message)

            return JsonResponse({
                'form_is_valid': True,
                'success': True
            })

        except Exception as e:
            print(f"❌ ERREUR dans form_valid: {str(e)}")
            import traceback
            traceback.print_exc()
            form.add_error(None, f"Erreur lors de la création : {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Retourner le formulaire avec erreurs"""
        print("=== form_invalid (CREATE) ===")
        print("Erreurs du formulaire:", form.errors)
        print("Erreurs non-field:", form.non_field_errors())
        
        html_form = render_to_string(
            self.template_name,
            {'form': form}, 
            request=self.request
        )
        
        
        return JsonResponse({
       'form_is_valid': True,
       'success': True  # ✅ Ajouté
   })


class IncidentUpdateView(BaseAjaxUpdateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'staff/incident_update.html'
    success_url = reverse_lazy('staff:incident_list')
    success_message = _('Incident mis à jour avec succès')

    def get_object(self):
        """Récupérer l'objet Incident"""
        return get_object_or_404(Incident, pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        """Charger le formulaire pré-rempli dans la modale"""
        print(f"=== GET IncidentUpdateView (PK={self.kwargs['pk']}) ===")
        print(f"Template utilisé: {self.template_name}")
        
        self.object = self.get_object()
        form = self.get_form()
        
        html_form = render_to_string(
            self.template_name,
            {'form': form, 'object': self.object},
            request=request
        )
        
        return JsonResponse({'html_form': html_form})

    def post(self, request, *args, **kwargs):
        """Traiter la soumission du formulaire de modification"""
        print(f"=== POST IncidentUpdateView (PK={self.kwargs['pk']}) ===")
        print("POST data:", request.POST)
        
        self.object = self.get_object()
        form = self.get_form()
        
        print("Form errors:", form.errors if not form.is_valid() else "Aucune erreur")
        
        if form.is_valid():
            print("✅ Formulaire valide")
            return self.form_valid(form)
        else:
            print("❌ Formulaire invalide")
            return self.form_invalid(form)

    def form_valid(self, form):
        """Sauvegarder les modifications"""
        try:
            print("=== form_valid (UPDATE) ===")
            instance = form.save(commit=False)
            instance.save()
            
            print(f"✅ Incident modifié: ID={instance.pk}, Employé={instance.employe}, Type={instance.type_incident}")
            
            # Message de succès
            if self.success_message:
                messages.success(self.request, self.success_message)

            return JsonResponse({
                'form_is_valid': True,
                'success': True
            })
            
        except Exception as e:
            print(f"❌ ERREUR dans form_valid: {str(e)}")
            import traceback
            traceback.print_exc()
            form.add_error(None, f"Erreur lors de la modification : {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Retourner le formulaire avec erreurs"""
        print("=== form_invalid (UPDATE) ===")
        print("Erreurs du formulaire:", form.errors)
        print("Erreurs non-field:", form.non_field_errors())
        
        html_form = render_to_string(
            self.template_name,
            {'form': form, 'object': self.object},
            request=self.request
        )
        
        return JsonResponse({
       'form_is_valid': True,
       'success': True  # ✅ Ajouté
   })


class IncidentDeleteView(DeleteView):
    model = Incident
    success_url = reverse_lazy('staff:incident_list')

    def post(self, request, *args, **kwargs):
        conge = self.get_object()
        conge.delete()
        return JsonResponse({'success': True})