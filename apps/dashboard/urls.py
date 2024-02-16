from django.urls import path, include
from .views import DashboardView


app_name = 'dashboard'

urlpatterns = [
    path('dashboard', DashboardView.as_view(), name='index')
]