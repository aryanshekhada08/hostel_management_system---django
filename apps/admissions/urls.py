from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_admission, name='submit_admission'),
]
