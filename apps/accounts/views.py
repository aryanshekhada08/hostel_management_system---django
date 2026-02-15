from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# ===============================
# STUDENT LOGIN
# ===============================
def student_login(request):

    # If already logged in → redirect properly
    if request.user.is_authenticated:
        if request.user.role == "STUDENT":
            return redirect("accounts:student_dashboard")
        return redirect("home")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None and user.role == "STUDENT":
            login(request, user)

            # Force password change if required
            if user.must_change_password:
                return redirect("accounts:change_password")

            return redirect("accounts:student_dashboard")

        messages.error(request, "Invalid credentials")

    return render(request, "accounts/student_login.html")


# ===============================
# STUDENT DASHBOARD
# ===============================
@login_required
def student_dashboard(request):

    # Extra protection
    if request.user.role != "STUDENT":
        return redirect("home")

    # Force password change
    if request.user.must_change_password:
        return redirect("accounts:change_password")

    return render(request, "dashboards/student/dashboard.html")


# ===============================
# CHANGE PASSWORD
# ===============================
@login_required
def change_password(request):

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("accounts:change_password")

        request.user.set_password(new_password)
        request.user.must_change_password = False
        request.user.save()

        messages.success(request, "Password changed successfully")
        return redirect("accounts:login")

    return render(request, "accounts/change_password.html")


# ===============================
# LOGOUT
# ===============================
@login_required
def logout_view(request):
    logout(request)
    return redirect("home")