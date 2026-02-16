from django.urls import path
from . import views

urlpatterns = [
    path('', views.wallet_dashboard, name='wallet_dashboard'),
    path('admin/dashboard/', views.admin_wallet_dashboard, name='admin_wallet_dashboard'),
    path('admin/add-money/', views.admin_add_money, name='admin_add_money'),
    path('admin/deduct/<int:user_id>/', views.admin_deduct_money, name='admin_deduct_money'),
]