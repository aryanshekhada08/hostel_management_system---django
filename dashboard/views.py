from apps.complaints.models import Complaint
from apps.fees.models import Payment
from apps.accounts.models import User
from django.db.models import Sum
from django.shortcuts import render
from apps.rooms.models import Room
from apps.accounts.models import User
from apps.fees.models import Payment
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.db.models.functions import TruncMonth




def admin_dashboard(request):

    

    # =======================
    # Stats Cards
    # =======================
    total_students = User.objects.filter(role="Student").count()
    total_complaints = Complaint.objects.count()
    pending_complaints = Complaint.objects.filter(status="Pending").count()
    total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0

    # =======================
    # Monthly Revenue Chart
    # =======================
    monthly_data = (
        Payment.objects
        .annotate(month=TruncMonth('payment_date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    months = [entry['month'].strftime("%b %Y") for entry in monthly_data]
    totals = [entry['total'] for entry in monthly_data]

    # =======================
    # Recent Activity
    # =======================
    recent_complaints = Complaint.objects.order_by('-created_at')[:5]
    recent_payments = Payment.objects.order_by('-payment_date')[:5]

    context = {
        "total_students": total_students,
        "total_complaints": total_complaints,
        "pending_complaints": pending_complaints,
        "total_revenue": total_revenue,
        "months": months,
        "totals": totals,
        "recent_complaints": recent_complaints,
        "recent_payments": recent_payments,
    }

    return render(request, "dashboards/admin_dashboard.html", context)
    
    

def admin_students(request):


    search_query = request.GET.get('search')

    students = User.objects.filter(role="Student")

    if search_query:
        students = students.filter(full_name__icontains=search_query)

    paginator = Paginator(students, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_query": search_query
    }

    return render(request, "dashboard/students.html", context)