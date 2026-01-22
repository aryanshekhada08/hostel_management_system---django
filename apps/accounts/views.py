from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def student_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.role != 'STUDENT':
                messages.error(request, 'Only students can login here.')
            else:
                login(request, user)
                return redirect('dashboards/student.html')
        else:
            messages.error(request, 'Invalid email or password')

    return render(request, 'accounts/student_login.html')



from django.contrib.auth.decorators import login_required

@login_required
def student_dashboard(request):
    return render(request, 'dashboards/student.html')