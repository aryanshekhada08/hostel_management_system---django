from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import Fee

User = get_user_model()

def is_admin(user):
    return user.is_superuser


@login_required
@user_passes_test(is_admin)
def fee_dashboard(request):

    if request.method == "POST":
        student_id = request.POST.get("student")
        amount = request.POST.get("amount")
        due_date = request.POST.get("due_date")

        student = User.objects.get(id=student_id)

        Fee.objects.create(
            student=student,
            amount=amount,
            due_date=due_date
        )

        messages.success(request, "Fee assigned successfully!")
        return redirect("fee_dashboard")

    fees = Fee.objects.select_related("student")
    students = User.objects.all()

    return render(request, "fees/fee_dashboard.html", {
        "fees": fees,
        "students": students
    })