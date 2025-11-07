from django.contrib import messages
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django_filters.views import FilterView
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django_filters import FilterSet,CharFilter
import django_filters

class BaseFilterSet(FilterSet):
    """FilterSet générique pour filtrage sur 'nom'."""
    nom = CharFilter(lookup_expr='icontains', label=_('Nom'))

    class Meta:
        model = None  # Défini dans la vue enfant
        fields = ['nom']

class BaseAjaxListView(FilterView):
    """ListView standardisée avec filtrage et pagination."""
    paginate_by = 10
    page_kwarg = 'page'
    filterset_class = BaseFilterSet
    context_object_name = 'objects'  # Générique ; overridez si needed

    def get_queryset(self):
        queryset = super().get_queryset().exclude(pk__isnull=True).order_by('-id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not context.get(self.context_object_name):
            context['empty_message'] = _('Aucun élément ne correspond aux critères.')
        return context

class AjaxFormMixin:
    """Mixin pour formulaires AJAX (déjà bon ; petit ajustement pour dynamique)."""
    template_name = None
    success_url = None  # À définir dans la vue enfant

    def get(self, request, *args, **kwargs):
        if isinstance(self, UpdateView):
            self.object = self.get_object()
        else:
            self.object = None

        form = self.get_form()
        context = {"form": form}
        data = {'html_form': render_to_string(self.template_name, context, request=request)}
        return JsonResponse(data)

    def form_invalid(self, form):
        context = {"form": form}
        data = {'form_is_valid': False, 'html_form': render_to_string(self.template_name, context, request=self.request)}
        return JsonResponse(data)

    def form_valid(self, form):
        form.save()
        data = {'form_is_valid': True, 'url_redirect': self.success_url}
        return JsonResponse(data)

class BaseAjaxCreateView(AjaxFormMixin, CreateView):
    """CreateView standardisée pour AJAX."""
    success_message = None  # Overridez

class BaseAjaxUpdateView(AjaxFormMixin, UpdateView):
    """UpdateView standardisée pour AJAX."""
    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])

class BaseAjaxDeleteView(DeleteView):
    """DeleteView standardisée pour suppression AJAX."""
    success_message = None  # Overridez dans l'enfant
    success_url = None  # URL de redirection post-suppression

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        if self.success_message:
            messages.success(request, self.success_message)
        data = {
            'url_redirect': success_url,
            'message': _('Élément supprimé avec succès !')
        }
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['POST'])