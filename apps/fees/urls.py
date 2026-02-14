from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.fee_dashboard, name='fee_dashboard'),
]