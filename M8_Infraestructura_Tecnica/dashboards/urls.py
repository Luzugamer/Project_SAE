from django.urls import path
from . import views

app_name = 'dashboards'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('list/', views.DashboardListView.as_view(), name='list'),
    # Agrega más rutas según necesites
]