from django.urls import path
from .views import (
    student_login,
    student_dashboard,
    change_password,
    logout_view,
)
from apps.accounts import views

app_name = "accounts"

urlpatterns = [
    path("login/", student_login, name="login"),
    path("logout/", logout_view, name="logout"),
    path("student-dashboard/", student_dashboard, name="student_dashboard"),
    path("change-password/", change_password, name="change_password"),
    path('profile/', views.my_profile, name='my_profile'),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("reset-password/", views.reset_password, name="reset_password"),
    

]