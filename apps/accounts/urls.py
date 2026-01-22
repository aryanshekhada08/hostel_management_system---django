from django.urls import path
from .views import student_dashboard, student_login

urlpatterns = [
    path('login/', student_login, name='student_login'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),

]
