# core/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import SystemConfig, ActionLog, Notification
from .forms import SystemConfigForm, ActionLogForm, NotificationForm


# ==================== SYSTEM CONFIG ====================
class ConfigListView(ListView):
    model = SystemConfig
    template_name = 'core/config_list.html'
    context_object_name = 'configs'
    ordering = ['cle']


class ConfigCreateView(CreateView):
    model = SystemConfig
    form_class = SystemConfigForm
    template_name = 'core/config_form.html'
    success_url = reverse_lazy('core:config_list')


class ConfigUpdateView(UpdateView):
    model = SystemConfig
    form_class = SystemConfigForm
    template_name = 'core/config_form.html'
    success_url = reverse_lazy('core:config_list')


class ConfigDeleteView(DeleteView):
    model = SystemConfig
    template_name = 'core/config_confirm_delete.html'
    success_url = reverse_lazy('core:config_list')


# ==================== ACTION LOG ====================
class LogListView(ListView):
    model = ActionLog
    template_name = 'core/log_list.html'
    context_object_name = 'logs'
    ordering = ['-date']
    paginate_by = 50  # 50 logs par page


# ==================== NOTIFICATION ====================
class NotifListView(ListView):
    model = Notification
    template_name = 'core/notif_list.html'
    context_object_name = 'notifications'
    ordering = ['-date']


class NotifCreateView(CreateView):
    model = Notification
    form_class = NotificationForm
    template_name = 'core/notif_form.html'
    success_url = reverse_lazy('core:notif_list')


class NotifUpdateView(UpdateView):
    model = Notification
    form_class = NotificationForm
    template_name = 'core/notif_form.html'
    success_url = reverse_lazy('core:notif_list')


class NotifDeleteView(DeleteView):
    model = Notification
    template_name = 'core/notif_confirm_delete.html'
    success_url = reverse_lazy('core:notif_list')