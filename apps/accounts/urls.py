from django.urls import path

from apps.admissions import views
from .views import change_password, logout_view, student_dashboard, student_login


urlpatterns = [
    path('login/', student_login, name='login'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('change-password/', change_password, name='change_password'),
    path('student-dashboard/', student_dashboard, name='student_dashboard'),
    # path('logout/', logout_view, name='logout'),
    # path('login/', views.login_view, name='login'),
    # path('logout/', views.logout_view, name='logout'),
    # path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
]
