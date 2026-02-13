from django.urls import path

from apps.admissions import views
from .views import change_password, student_dashboard, student_login


urlpatterns = [
    path('login/', student_login, name='student_login'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('change-password/', change_password, name='change_password'),

]
