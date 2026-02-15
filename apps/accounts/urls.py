from django.urls import path
from .views import (
    student_login,
    student_dashboard,
    change_password,
    logout_view,
)

app_name = "accounts"

urlpatterns = [
    path("login/", student_login, name="login"),
    path("logout/", logout_view, name="logout"),
    path("student-dashboard/", student_dashboard, name="student_dashboard"),
    path("change-password/", change_password, name="change_password"),
]