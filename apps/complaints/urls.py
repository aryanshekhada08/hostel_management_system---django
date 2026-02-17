from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_complaint, name='submit_complaint'),
    path('my/', views.my_complaints, name='my_complaints'),
    path('admin/', views.admin_complaints, name='admin_complaints'),
    path('admin/<int:id>/', views.complaint_detail, name='complaint_detail'),
]