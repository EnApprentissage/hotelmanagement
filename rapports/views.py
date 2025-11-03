# rapports/views.py
from django.shortcuts import render, get_object_or_404
from .models import DailyReport
from datetime import datetime
from django.core.paginator import Paginator

def daily_reports_list(request):
    """
    Affiche la liste des rapports journaliers avec option de filtrage par date.
    """
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    reports = DailyReport.objects.all().order_by('-date')

    # Filtrage par période
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            reports = reports.filter(date__gte=start_date_obj)
        except ValueError:
            pass

    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            reports = reports.filter(date__lte=end_date_obj)
        except ValueError:
            pass

    # Pagination (10 rapports par page)
    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'reports': page_obj,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'rapports/daily_reports_list.html', context)


def daily_report_detail(request, pk):
    """
    Affiche le détail d'un rapport journalier.
    """
    report = get_object_or_404(DailyReport, pk=pk)
    return render(request, 'rapports/daily_report_detail.html', {'report': report})


# Rapports spécifiques pour le menu CoreUI

def rapport_occupation(request):
    reports = DailyReport.objects.all().order_by('-date')
    return render(request, 'rapports/rapport_occupation.html', {'reports': reports})


def rapport_ca(request):
    reports = DailyReport.objects.all().order_by('-date')
    return render(request, 'rapports/rapport_ca.html', {'reports': reports})


def rapport_reservations(request):
    reports = DailyReport.objects.all().order_by('-date')
    return render(request, 'rapports/rapport_reservations.html', {'reports': reports})


def rapport_financier(request):
    reports = DailyReport.objects.all().order_by('-date')
    return render(request, 'rapports/rapport_financier.html', {'reports': reports})


def meilleurs_clients(request):
    # Exemple : top 10 clients selon nouveaux clients
    clients = DailyReport.objects.order_by('-clients_nouveaux')[:10]
    return render(request, 'rapports/meilleurs_clients.html', {'clients': clients})


def export_donnees(request):
    """
    Page pour exporter les données (CSV / Excel).
    """
    # Ici tu pourras implémenter l'export réel
    return render(request, 'rapports/export_donnees.html')
