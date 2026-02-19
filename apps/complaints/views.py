from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Complaint

@login_required
def submit_complaint(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        description = request.POST.get('description')
        room_number = request.POST.get('room_number')

        Complaint.objects.create(
            student=request.user,
            title=title,
            category=category,
            description=description,
            room_number=room_number
        )

        return redirect('my_complaints')

    return render(request, 'complaints/submit_complaint.html')


@login_required
def my_complaints(request):
    complaints = Complaint.objects.filter(student=request.user)
    return render(request, 'complaints/my_complaints.html', {'complaints': complaints})




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Complaint


# Admin Complaint List
# @login_required
def admin_complaints(request):
   

    complaints = Complaint.objects.all().order_by('-created_at')
    return render(request, 'complaints/admin_complaints.html', {'complaints': complaints})


# Admin Complaint Detail
# @login_required
def complaint_detail(request, id):
    

    complaint = get_object_or_404(Complaint, id=id)

    if request.method == "POST":
        status = request.POST.get("status")
        complaint.status = status
        complaint.save()
        return redirect('admin_complaints')

    return render(request, 'complaints/complaint_detail.html', {'complaint': complaint})