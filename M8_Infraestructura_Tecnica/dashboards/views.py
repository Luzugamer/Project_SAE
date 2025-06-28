from django.shortcuts import render
from django.views.generic import ListView
from .models import Dashboard

def dashboard_index(request):
    return render(request, 'dashboards/index.html', {'title': 'Panel Principal'})

class DashboardListView(ListView):
    model = Dashboard
    template_name = 'dashboards/list.html'
    context_object_name = 'dashboards'