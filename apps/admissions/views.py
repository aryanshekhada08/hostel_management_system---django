from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import AdmissionForm
from .models import Admission

from apps.accounts.permissions import student_required

@login_required
@student_required
def submit_admission(request):

    # Student can submit only once
    if hasattr(request.user, 'admission'):
        return render(request, 'admissions/already_submitted.html')

    if request.method == 'POST':
        form = AdmissionForm(request.POST, request.FILES)
        if form.is_valid():
            admission = form.save(commit=False)
            admission.student = request.user
            admission.save()
            return redirect('student_dashboard')
    else:
        form = AdmissionForm()

    return render(request, 'admissions/submit.html', {'form': form})
