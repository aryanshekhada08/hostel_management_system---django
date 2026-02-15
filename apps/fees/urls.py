from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.fee_dashboard, name='fee_dashboard'),
    path("pay/<int:fee_id>/", views.pay_fee, name="pay_fee"),
    path("edit/<int:fee_id>/", views.edit_fee, name="edit_fee"),
    path("delete/<int:fee_id>/", views.delete_fee, name="delete_fee"),
    path("student-history/", views.student_fee_history, name="student_fee_history"),
    path("add/", views.add_fee, name="add_fee"),
    path("payments/", views.payment_history, name="payment_history"),
    path("receipt/<int:payment_id>/", views.download_receipt, name="download_receipt"),
   
]