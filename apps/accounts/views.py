from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required



def student_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # user = authenticate(request, email=email, password=password)
        user = authenticate(request, username=email, password=password)

        if user is not None and user.role == 'STUDENT':
            login(request, user)

            # 🔐 FORCE PASSWORD CHANGE
            if user.must_change_password:
                return redirect('change_password')

            return redirect('student_dashboard')

        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'accounts/student_login.html')


@login_required
def student_dashboard(request):

    if request.user.must_change_password:
        return redirect('change_password')

    return render(request, 'dashboards/student/dashboard.html')


@login_required
def change_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('change_password')

        request.user.set_password(new_password)
        request.user.must_change_password = False
        request.user.save()

        messages.success(request, "Password changed successfully")
        return redirect('student_login')

    return render(request, 'accounts/change_password.html')