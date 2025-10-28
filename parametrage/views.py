# parametrage/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import GlobalVariables
from .forms import GlobalVariablesForm  # ← Ton forms.py


# ==================== VUES ====================
class VariablesListView(ListView):
    model = GlobalVariables
    template_name = 'parametrage/variables_list.html'
    context_object_name = 'variables'
    ordering = ['group', 'cle']


class VariablesCreateView(CreateView):
    model = GlobalVariables
    form_class = GlobalVariablesForm
    template_name = 'parametrage/variables_form.html'
    success_url = reverse_lazy('parametrage:variables_list')


class VariablesUpdateView(UpdateView):
    model = GlobalVariables
    form_class = GlobalVariablesForm
    template_name = 'parametrage/variables_form.html'
    success_url = reverse_lazy('parametrage:variables_list')


class VariablesDeleteView(DeleteView):
    model = GlobalVariables
    template_name = 'parametrage/variables_confirm_delete.html'
    success_url = reverse_lazy('parametrage:variables_list')