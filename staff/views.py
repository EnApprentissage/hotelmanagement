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
from django.views.decorators.http import require_POST


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
    paginate_by = 15 # ← nombre d’employés par page
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
        """Charger le formulaire vierge dans la modale (AJAX)"""
        print("=== GET EmployeCreateView ===")

        self.object = None
        form = self.get_form()

        html_form = render_to_string(
            self.template_name,
            {'form': form},
            request=request
        )

        return JsonResponse({'html_form': html_form})

    def post(self, request, *args, **kwargs):
        """Traiter la soumission AJAX"""
        print("=== POST EmployeCreateView ===")
        print("POST DATA:", request.POST)

        self.object = None
        form = self.get_form()

        if form.is_valid():
            print("Formulaire valide")
            return self.form_valid(form)
        else:
            print("Formulaire invalide:", form.errors)
            return self.form_invalid(form)

    def form_valid(self, form):
        """Sauvegarde finale"""
        try:
            print("=== form_valid EMPLOYE CREATE ===")

            instance = form.save(commit=False)
            instance.user_id = self.request.user.id
            instance.save()

            print(f"Employé créé: {instance.nom} {instance.prenom}")

            return JsonResponse({
                'form_is_valid': True,
                'success': True
            })

        except Exception as e:
            print("ERREUR :", e)
            form.add_error(None, f"Erreur lors de la création : {e}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Retourner le formulaire avec erreurs - même format que Conge/Incident"""
        print("=== form_invalid EMPLOYE CREATE ===")
        print("Erreurs:", form.errors)

        html_form = render_to_string(
            self.template_name,
            {'form': form},
            request=self.request
        )

        return JsonResponse({
            'form_is_valid': False,
            'success': False,
            'html_form': html_form
        })


class EmployeUpdateView(BaseAjaxUpdateView):
    model = Employe
    form_class = EmployeForm
    template_name = StaffTemplate.update_template
    success_url = reverse_lazy('staff:employe_list')
    success_message = _('Employé mis à jour avec succès')

    def dispatch(self, request, *args, **kwargs):
        """Bloquer COMPLÈTEMENT l'accès si verrouillé"""
        employe = self.get_object()
        
        # 🔥 BLOQUER MÊME LE GET si verrouillé
        if employe.is_locked:
            if request.method == 'GET':
                # Retourner un formulaire en lecture seule
                return JsonResponse({
                    'html_form': self.get_locked_form_html(employe),
                    'is_locked': True
                })
            else:
                # Bloquer complètement le POST
                return JsonResponse({
                    'form_is_valid': False,
                    'success': False,
                    'error': '🔒 Cette fiche est verrouillée et ne peut plus être modifiée.',
                    'is_locked': True
                })
        
        return super().dispatch(request, *args, **kwargs)

    def get_locked_form_html(self, employe):
        """Générer un formulaire verrouillé en lecture seule"""
        html = f"""
        <div class="modal-header bg-warning">
            <h5 class="modal-title">
                <i class="fas fa-lock"></i> Fiche Verrouillée
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
            <div class="alert alert-warning">
                <i class="fas fa-lock me-2"></i>
                <strong>Cette fiche est verrouillée</strong> et ne peut plus être modifiée.
            </div>
            
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label fw-bold">Nom</label>
                    <p class="form-control-plaintext">{employe.nom}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Prénom</label>
                    <p class="form-control-plaintext">{employe.prenom}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Matricule</label>
                    <p class="form-control-plaintext">{employe.matricule}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Poste</label>
                    <p class="form-control-plaintext">{employe.poste}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Email</label>
                    <p class="form-control-plaintext">{employe.email}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Téléphone</label>
                    <p class="form-control-plaintext">{employe.phone}</p>
                </div>
            </div>
        </div>
        <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                <i class="fas fa-times"></i> Fermer
            </button>
        </div>
        """
        return html

    def get_form(self, form_class=None):
        """Désactiver tous les champs si verrouillé"""
        form = super().get_form(form_class)
        if self.object and self.object.is_locked:
            for field in form.fields:
                form.fields[field].disabled = True
                form.fields[field].widget.attrs['readonly'] = True
        return form

    def post(self, request, *args, **kwargs):
        """Soumission AJAX de la modification"""
        self.object = self.get_object()
        
        print("=== POST REQUEST ===")
        print("POST data:", request.POST)
        print("validate_lock présent?", 'validate_lock' in request.POST)
        
        # 🔒 DÉTECTER LE BOUTON "Valider et Verrouiller"
        if 'validate_lock' in request.POST:
            print("=== VERROUILLAGE DÉTECTÉ ===")
            self.object.is_locked = True
            self.object.save(update_fields=['is_locked'])
            print(f"=== Employé {self.object.pk} verrouillé ===")
            
            return JsonResponse({
                'form_is_valid': True,
                'success': True,
                'locked': True,
                'message': f'🔒 Fiche de {self.object.get_full_name()} verrouillée avec succès.',
            })
        
        # Sinon, traitement normal du formulaire
        print("=== MISE À JOUR NORMALE ===")
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            print("Erreurs formulaire:", form.errors)
            return self.form_invalid(form)

    def form_valid(self, form):
        """Sauvegarder les modifications"""
        instance = form.save()
        print(f"=== Employé {instance.pk} mis à jour ===")

        return JsonResponse({
            'form_is_valid': True,
            'success': True,
            'message': self.success_message
        })

    def form_invalid(self, form):
        """Retourner le formulaire avec erreurs"""
        html_form = render_to_string(
            self.template_name,
            {'form': form, 'object': self.object},
            request=self.request
        )

        return JsonResponse({
            'form_is_valid': False,
            'success': False,
            'html_form': html_form
        })
    
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
    paginate_by = 15

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
    template_name = 'staff/planning_update.html'  # 🔥 CHANGÉ ICI
    success_url = reverse_lazy('staff:planning_list')
    success_message = _('Planning mis à jour avec succès')

    def get_object(self):
        """Récupérer l'objet Planning"""
        return get_object_or_404(Planning, pk=self.kwargs['pk'])

    def dispatch(self, request, *args, **kwargs):
        """Bloquer COMPLÈTEMENT l'accès si verrouillé"""
        planning = self.get_object()
        
        if planning.is_locked:
            if request.method == 'GET':
                # Retourner un formulaire en lecture seule
                return JsonResponse({
                    'html_form': self.get_locked_form_html(planning),
                    'is_locked': True
                })
            else:
                # Bloquer complètement le POST
                return JsonResponse({
                    'form_is_valid': False,
                    'success': False,
                    'error': '🔒 Ce planning est verrouillé et ne peut plus être modifié.',
                    'is_locked': True
                })
        
        return super().dispatch(request, *args, **kwargs)

    def get_locked_form_html(self, planning):
        """Générer un formulaire verrouillé en lecture seule"""
        html = f"""
        <div class="modal-header bg-warning text-white">
            <h5 class="modal-title">
                <i class="fas fa-lock"></i> Planning Verrouillé
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
            <div class="alert alert-warning">
                <i class="fas fa-lock me-2"></i>
                <strong>Ce planning est verrouillé</strong> et ne peut plus être modifié.
            </div>
            
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label fw-bold">Employé</label>
                    <p class="form-control-plaintext">{planning.employe.get_full_name()}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Date</label>
                    <p class="form-control-plaintext">{planning.date.strftime('%d/%m/%Y')}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Période</label>
                    <p class="form-control-plaintext">{planning.get_periode_display()}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Heure début</label>
                    <p class="form-control-plaintext">{planning.heure_debut.strftime('%H:%M')}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Heure fin</label>
                    <p class="form-control-plaintext">{planning.heure_fin.strftime('%H:%M')}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Poste assigné</label>
                    <p class="form-control-plaintext">{planning.poste_assigne or '—'}</p>
                </div>
            </div>
        </div>
        <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                <i class="fas fa-times"></i> Fermer
            </button>
        </div>
        """
        return html

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
        
        # 🔒 Si bouton "Valider et verrouiller"
        if 'validate_lock' in request.POST:
            self.object.is_locked = True
            self.object.save(update_fields=['is_locked'])
            print(f"✅ Planning verrouillé: ID={self.object.pk}")
            return JsonResponse({
                'form_is_valid': True,
                'success': True,
                'locked': True,
                'message': f'🔒 Planning du {self.object.date.strftime("%d/%m/%Y")} verrouillé avec succès.',
            })
        
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
            
            if self.success_message:
                messages.success(self.request, self.success_message)

            return JsonResponse({
                'form_is_valid': True,
                'success': True,
                'message': self.success_message
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
            'form_is_valid': False,
            'success': False,
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
    ordering = ['-date_debut']
    paginate_by = 15

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
    template_name = 'staff/conge_create.html'
    success_url = reverse_lazy('staff:conge_list')
    success_message = _('Congé créé avec succès')

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
        return self.form_invalid(form)

    def form_valid(self, form):
        """Sauvegarder et renvoyer JSON pour AJAX"""
        instance = form.save(commit=False)

        # Assigner l'utilisateur si nécessaire
        if hasattr(instance, 'user_id') and not instance.user_id:
            instance.user_id = self.request.user.id

        instance.save()

        return JsonResponse({
            'form_is_valid': True,
            'success': True,
            'url_redirect': str(self.success_url),  # <-- Ajouté pour redirection AJAX
        })

    def form_invalid(self, form):
        """Retourner le formulaire avec erreurs pour AJAX"""
        html_form = render_to_string(
            self.template_name,
            {'form': form}, 
            request=self.request
        )
        return JsonResponse({
            'form_is_valid': False,  # ✅ corrigé
            'success': False,        # ✅ corrigé
            'html_form': html_form
        })



class CongeUpdateView(BaseAjaxUpdateView):
    model = Conge
    form_class = CongeForm
    template_name = 'staff/conge_update.html'
    success_url = reverse_lazy('staff:conge_list')
    success_message = _('Congé mis à jour avec succès')

    def get_object(self):
        """Récupérer l'objet Conge"""
        return get_object_or_404(Conge, pk=self.kwargs['pk'])

    def dispatch(self, request, *args, **kwargs):
        """Bloquer COMPLÈTEMENT l'accès si verrouillé"""
        conge = self.get_object()
        
        if conge.is_locked:
            if request.method == 'GET':
                return JsonResponse({
                    'html_form': self.get_locked_form_html(conge),
                    'is_locked': True
                })
            else:
                return JsonResponse({
                    'form_is_valid': False,
                    'success': False,
                    'error': '🔒 Ce congé est verrouillé et ne peut plus être modifié.',
                    'is_locked': True
                })
        
        return super().dispatch(request, *args, **kwargs)

    def get_locked_form_html(self, conge):
        """Générer un formulaire verrouillé en lecture seule"""
        html = f"""
        <div class="modal-header bg-warning text-white">
            <h5 class="modal-title">
                <i class="fas fa-lock"></i> Congé Verrouillé
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
            <div class="alert alert-warning">
                <i class="fas fa-lock me-2"></i>
                <strong>Ce congé est verrouillé</strong> et ne peut plus être modifié.
            </div>
            
            <div class="row g-3">
                <div class="col-md-12">
                    <label class="form-label fw-bold">Employé</label>
                    <p class="form-control-plaintext">{conge.employe.get_full_name()}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Type</label>
                    <p class="form-control-plaintext">{conge.get_type_conge_display()}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Statut</label>
                    <p class="form-control-plaintext">{conge.get_statut_display()}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Date début</label>
                    <p class="form-control-plaintext">{conge.date_debut.strftime('%d/%m/%Y')}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Date fin</label>
                    <p class="form-control-plaintext">{conge.date_fin.strftime('%d/%m/%Y')}</p>
                </div>
                <div class="col-md-12">
                    <label class="form-label fw-bold">Nombre de jours</label>
                    <p class="form-control-plaintext">{conge.nombre_jours} jour(s)</p>
                </div>
                <div class="col-md-12">
                    <label class="form-label fw-bold">Motif</label>
                    <p class="form-control-plaintext">{conge.motif}</p>
                </div>
            </div>
        </div>
        <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                <i class="cil-x"></i> Fermer
            </button>
        </div>
        """
        return html

    def get(self, request, *args, **kwargs):
        """Charger le formulaire pré-rempli dans la modale"""
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
        self.object = self.get_object()
        
        # 🔒 Si bouton "Valider et verrouiller"
        if 'validate_lock' in request.POST:
            self.object.is_locked = True
            self.object.save(update_fields=['is_locked'])
            return JsonResponse({
                'form_is_valid': True,
                'success': True,
                'locked': True,
                'message': f'🔒 Congé de {self.object.employe.get_full_name()} verrouillé avec succès.',
            })
        
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        """Sauvegarder les modifications et renvoyer JSON pour AJAX"""
        instance = form.save(commit=False)
        instance.save()

        return JsonResponse({
            'form_is_valid': True,
            'success': True,
            'message': self.success_message
        })

    def form_invalid(self, form):
        """Retourner le formulaire avec erreurs pour AJAX"""
        html_form = render_to_string(
            self.template_name,
            {'form': form, 'object': self.object},
            request=self.request
        )
        return JsonResponse({
            'form_is_valid': False,
            'success': False,
            'html_form': html_form
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
    paginate_by = 15

    def get_queryset(self):
        queryset = Evaluation.objects.select_related('employe', 'evaluateur').all()
        
        # Recherche unifiée
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(employe__nom__icontains=search) |
                Q(employe__prenom__icontains=search) |
                Q(employe__matricule__icontains=search) |
                Q(employe__poste__icontains=search)
            )
        
        # Filtre par poste
        poste = self.request.GET.get('poste', '').strip()
        if poste:
            queryset = queryset.filter(employe__poste__icontains=poste)
        
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['postes'] = Employe.objects.values_list('poste', flat=True).distinct().order_by('poste')
        return context


class EvaluationCreateView(BaseAjaxCreateView):
    model = Evaluation
    form_class = EvaluationForm
    template_name = 'staff/evaluation_create.html'
    success_url = reverse_lazy('staff:evaluation_list')

    def form_valid(self, form):
        instance = form.save(commit=False)
        if not instance.evaluateur:
            instance.evaluateur = self.request.user
        instance.save()
        return JsonResponse({'form_is_valid': True, 'success': True,'url_redirect': str(self.success_url)})

    def form_invalid(self, form):
        html_form = render_to_string(self.template_name, {'form': form}, request=self.request)
        return JsonResponse({'form_is_valid': False, 'success': False, 'html_form': html_form})


class EvaluationUpdateView(BaseAjaxUpdateView):
    model = Evaluation
    form_class = EvaluationForm
    template_name = 'staff/evaluation_update.html'
    success_url = reverse_lazy('staff:evaluation_list')
    success_message = _('Évaluation mise à jour avec succès')

    def get_object(self):
        """Récupérer l'objet Evaluation"""
        return get_object_or_404(Evaluation, pk=self.kwargs['pk'])

    def dispatch(self, request, *args, **kwargs):
        """Bloquer COMPLÈTEMENT l'accès si verrouillé"""
        evaluation = self.get_object()
        
        if evaluation.is_locked:
            if request.method == 'GET':
                return JsonResponse({
                    'html_form': self.get_locked_form_html(evaluation),
                    'is_locked': True
                })
            else:
                return JsonResponse({
                    'form_is_valid': False,
                    'success': False,
                    'error': '🔒 Cette évaluation est verrouillée et ne peut plus être modifiée.',
                    'is_locked': True
                })
        
        return super().dispatch(request, *args, **kwargs)

    def get_locked_form_html(self, evaluation):
        """Générer un formulaire verrouillé en lecture seule"""
        html = f"""
        <div class="modal-header bg-info text-white">
            <h5 class="modal-title">
                <i class="fas fa-lock"></i> Évaluation Verrouillée
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
            <div class="alert alert-warning">
                <i class="fas fa-lock me-2"></i>
                <strong>Cette évaluation est verrouillée</strong> et ne peut plus être modifiée.
            </div>
            
            <div class="row g-3">
                <div class="col-md-12">
                    <label class="form-label fw-bold">Employé</label>
                    <p class="form-control-plaintext">{evaluation.employe.get_full_name()}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Date évaluation</label>
                    <p class="form-control-plaintext">{evaluation.date_evaluation.strftime('%d/%m/%Y')}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Période évaluée</label>
                    <p class="form-control-plaintext">{evaluation.periode_evaluee}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Note globale</label>
                    <p class="form-control-plaintext">{evaluation.note_globale or '—'}/10</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Évaluateur</label>
                    <p class="form-control-plaintext">{evaluation.evaluateur.get_full_name() if evaluation.evaluateur else '—'}</p>
                </div>
            </div>
        </div>
        <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                <i class="cil-x"></i> Fermer
            </button>
        </div>
        """
        return html

    def get(self, request, *args, **kwargs):
        """Charger le formulaire pré-rempli dans la modale"""
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
        self.object = self.get_object()
        
        # 🔒 Si bouton "Valider et verrouiller"
        if 'validate_lock' in request.POST:
            self.object.is_locked = True
            self.object.save(update_fields=['is_locked'])
            return JsonResponse({
                'form_is_valid': True,
                'success': True,
                'locked': True,
                'message': f'🔒 Évaluation de {self.object.employe.get_full_name()} verrouillée avec succès.',
            })
        
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        """Sauvegarder les modifications et renvoyer JSON pour AJAX"""
        instance = form.save(commit=False)
        instance.save()

        return JsonResponse({
            'form_is_valid': True,
            'success': True,
            'message': self.success_message
        })

    def form_invalid(self, form):
        """Retourner le formulaire avec erreurs pour AJAX"""
        html_form = render_to_string(
            self.template_name,
            {'form': form, 'object': self.object},
            request=self.request
        )
        return JsonResponse({
            'form_is_valid': False,
            'success': False,
            'html_form': html_form
        })

class EvaluationDetailView(DetailView):
    model = Evaluation
    template_name = 'staff/evaluation_detail.html'
    context_object_name = 'evaluation'


class EvaluationDeleteView(BaseAjaxDeleteView):
    model = Evaluation
    success_url = reverse_lazy('staff:evaluation_list')

    def post(self, request, *args, **kwargs):
        evaluation = self.get_object()
        evaluation.delete()
        return JsonResponse({'success': True})

# ==================== INCIDENT ====================
class IncidentListView(ListView):
    model = Incident
    template_name = 'staff/incident_list.html'
    context_object_name = 'incidents'
    ordering = ['-date_incident']
    paginate_by = 15

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
        return self.form_invalid(form)

    def form_valid(self, form):
        """Sauvegarder et renvoyer JSON pour AJAX"""
        instance = form.save(commit=False)
        instance.signale_par = self.request.user
        instance.save()


        return JsonResponse({
            'form_is_valid': True,
            'success': True,
            'url_redirect': str(self.success_url),  # <-- Ajouté pour redirection AJAX
        })

    def form_invalid(self, form):
        """Retourner le formulaire avec erreurs pour AJAX"""
        html_form = render_to_string(
            self.template_name,
            {'form': form}, 
            request=self.request
        )
        return JsonResponse({
            'form_is_valid': False,  # ✅ corrigé
            'success': False,        # ✅ corrigé
            'html_form': html_form
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

    def dispatch(self, request, *args, **kwargs):
        """Bloquer COMPLÈTEMENT l'accès si verrouillé"""
        incident = self.get_object()
        
        if incident.is_locked:
            if request.method == 'GET':
                return JsonResponse({
                    'html_form': self.get_locked_form_html(incident),
                    'is_locked': True
                })
            else:
                return JsonResponse({
                    'form_is_valid': False,
                    'success': False,
                    'error': '🔒 Cet incident est verrouillé et ne peut plus être modifié.',
                    'is_locked': True
                })
        
        return super().dispatch(request, *args, **kwargs)

    def get_locked_form_html(self, incident):
        """Générer un formulaire verrouillé en lecture seule"""
        html = f"""
        <div class="modal-header bg-warning text-white">
            <h5 class="modal-title">
                <i class="fas fa-lock"></i> Incident Verrouillé
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
            <div class="alert alert-warning">
                <i class="fas fa-lock me-2"></i>
                <strong>Cet incident est verrouillé</strong> et ne peut plus être modifié.
            </div>
            
            <div class="row g-3">
                <div class="col-md-12">
                    <label class="form-label fw-bold">Employé</label>
                    <p class="form-control-plaintext">{incident.employe.get_full_name()}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Date incident</label>
                    <p class="form-control-plaintext">{incident.date_incident.strftime('%d/%m/%Y')}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Type</label>
                    <p class="form-control-plaintext">{incident.get_type_incident_display()}</p>
                </div>
                <div class="col-md-12">
                    <label class="form-label fw-bold">Description</label>
                    <p class="form-control-plaintext">{incident.description}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Sanction</label>
                    <p class="form-control-plaintext">{incident.get_sanction_display() if incident.sanction else '—'}</p>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-bold">Date sanction</label>
                    <p class="form-control-plaintext">{incident.date_sanction.strftime('%d/%m/%Y') if incident.date_sanction else '—'}</p>
                </div>
            </div>
        </div>
        <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                <i class="cil-x"></i> Fermer
            </button>
        </div>
        """
        return html

    def get(self, request, *args, **kwargs):
        """Charger le formulaire pré-rempli dans la modale"""
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
        self.object = self.get_object()
        
        # 🔒 Si bouton "Valider et verrouiller"
        if 'validate_lock' in request.POST:
            self.object.is_locked = True
            self.object.save(update_fields=['is_locked'])
            return JsonResponse({
                'form_is_valid': True,
                'success': True,
                'locked': True,
                'message': f'🔒 Incident verrouillé avec succès.',
            })
        
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        """Sauvegarder les modifications et renvoyer JSON pour AJAX"""
        instance = form.save(commit=False)
        instance.save()

        return JsonResponse({
            'form_is_valid': True,
            'success': True,
            'message': self.success_message
        })

    def form_invalid(self, form):
        """Retourner le formulaire avec erreurs pour AJAX"""
        html_form = render_to_string(
            self.template_name,
            {'form': form, 'object': self.object},
            request=self.request
        )
        return JsonResponse({
            'form_is_valid': False,
            'success': False,
            'html_form': html_form
        })


    
class IncidentDeleteView(DeleteView):
    model = Incident
    success_url = reverse_lazy('staff:incident_list')

    def post(self, request, *args, **kwargs):
        incident = self.get_object()
        incident.delete()
        return JsonResponse({'success': True})