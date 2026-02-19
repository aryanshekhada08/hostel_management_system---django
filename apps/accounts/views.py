from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.complaints.models import Complaint
from apps.notifications.models import Notification
from apps.rooms.models import RoomAllocation

from apps.rooms.models import RoomAllocation
from apps.fees.models import Fee
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .models import ContactMessage, User


from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import PasswordResetOTP

from django.db.models import Sum
from apps.wallets.models import Wallet, WalletTransaction
from apps.fees.models import Fee
from django.contrib.auth.decorators import login_required



from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import fonts
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.platypus import ListFlowable, ListItem
from reportlab.platypus import FrameBreak
from django.http import HttpResponse
from datetime import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from apps.wallets.models import WalletTransaction
from apps.fees.models import Fee
from apps.accounts.models import User

from datetime import datetime
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum

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

    if request.user.role != "STUDENT":
        return redirect("home")

    if request.user.must_change_password:
        return redirect("accounts:change_password")

    # 🏠 Get Room
    allocation = RoomAllocation.objects.filter(
        student=request.user
    ).select_related("room").first()

    room_number = allocation.room.room_number if allocation else None

    # 💰 Get Latest Fee
    fee = Fee.objects.filter(
        student=request.user
    ).order_by("-created_at").first()

    # 📩 Complaints
    complaints = Complaint.objects.filter(student=request.user)

    complaints_count = complaints.count()
    pending_count = complaints.filter(status__icontains="pending").count()
    resolved_count = complaints.filter(status__icontains="resolved").count()

    # 🔔 Notifications
    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    context = {
        "room_number": room_number,
        "fee": fee,
        "unread_count": unread_count,
        "complaints_count": complaints_count,
        "pending_count": pending_count,
        "resolved_count": resolved_count,
    }

    return render(request, "dashboards/student/dashboard.html", context)


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





def contact(request):

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        # Save in database
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        # Send email to admin
        send_mail(
            subject=f"Contact Form: {subject}",
            message=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )

        messages.success(request, "Your message has been sent successfully!")

    return render(request, "contact.html")


def my_profile(request):
        return render(request, "accounts/my_profile.html", {
            "user_obj": request.user
        })




from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import PasswordResetOTP


def forgot_password(request):

    if request.method == "POST":
        email = request.POST.get("email")

        user = User.objects.filter(email=email).first()

        if user:
            otp = PasswordResetOTP.generate_otp()

            PasswordResetOTP.objects.create(
                user=user,
                otp=otp
            )

            send_mail(
                "Your Password Reset OTP",
                f"Your OTP is: {otp}\nValid for 5 minutes.",
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )

            request.session["reset_user"] = user.id

        # 🔒 Always show same message
        messages.success(
            request,
            "If this email exists, an OTP has been sent."
        )

        return redirect("accounts:verify_otp")

    return render(request, "accounts/forgot_password.html")


def verify_otp(request):

    user_id = request.session.get("reset_user")

    if not user_id:
        return redirect("accounts:forgot_password")

    user = User.objects.get(id=user_id)

    if request.method == "POST":
        entered_otp = request.POST.get("otp")

        otp_obj = PasswordResetOTP.objects.filter(
            user=user
        ).last()

        if otp_obj and not otp_obj.is_expired() and otp_obj.otp == entered_otp:
            request.session["otp_verified"] = True
            return redirect("accounts:reset_password")

        messages.error(request, "Invalid or expired OTP")

    return render(request, "accounts/verify_otp.html")

from django.contrib.auth.hashers import make_password

def reset_password(request):

    if not request.session.get("otp_verified"):
        return redirect("accounts:forgot_password")

    user_id = request.session.get("reset_user")
    user = User.objects.get(id=user_id)

    if request.method == "POST":
        new_password = request.POST.get("password")

        user.password = make_password(new_password)
        user.must_change_password = False
        user.save()

        # Clear session
        request.session.flush()

        return redirect("accounts:login")

    return render(request, "accounts/reset_password.html")


@login_required
def financial_report(request):

    if request.user.role != "STUDENT":
        return redirect("home")

    # Wallet
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.all().order_by("-created_at")

    total_credit = wallet.transactions.filter(
        transaction_type="CREDIT"
    ).aggregate(Sum("amount"))["amount__sum"] or 0

    total_debit = wallet.transactions.filter(
        transaction_type="DEBIT"
    ).aggregate(Sum("amount"))["amount__sum"] or 0

    # Fees
    fees = Fee.objects.filter(student=request.user)

    total_fees_paid = fees.filter(status="Paid").aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    total_fees_pending = fees.filter(status="Pending").aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    context = {
        "wallet": wallet,
        "transactions": transactions,
        "total_credit": total_credit,
        "total_debit": total_debit,
        "total_fees_paid": total_fees_paid,
        "total_fees_pending": total_fees_pending,
    }

    return render(request, "accounts/financial_report.html", context)


def download_financial_report(request):
    # 1. Setup Response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Apex_Report_{request.user.full_name}.pdf"'

    doc = SimpleDocTemplate(
        response, 
        pagesize=A4,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=30
    )
    elements = []

    # 2. Define Theme Colors (Fixed HexColor capitalization)
    primary_indigo = colors.HexColor("#4f46e5")
    success_emerald = colors.HexColor("#10b981")
    warning_amber = colors.HexColor("#f59e0b")
    border_slate = colors.HexColor("#e2e8f0")

    # 3. Setup Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title', parent=styles['Heading1'], fontSize=22, textColor=primary_indigo, spaceAfter=5
    )
    label_style = ParagraphStyle(
        'Label', parent=styles['Normal'], fontSize=9, textColor=colors.grey, leading=12
    )
    value_style = ParagraphStyle(
        'Value', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', leading=14
    )

    # 4. Fetch Data
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    
    total_credit = wallet.transactions.filter(transaction_type="CREDIT").aggregate(Sum("amount"))["amount__sum"] or 0
    total_debit = wallet.transactions.filter(transaction_type="DEBIT").aggregate(Sum("amount"))["amount__sum"] or 0
    
    fees = Fee.objects.filter(student=request.user)
    total_fees_paid = fees.filter(status="Paid").aggregate(Sum("amount"))["amount__sum"] or 0
    total_fees_pending = fees.filter(status="Pending").aggregate(Sum("amount"))["amount__sum"] or 0

    # 5. Header Section
    elements.append(Paragraph("Student Financial Statement", title_style))
    elements.append(Paragraph("Apex Hostel Management System", label_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(HRFlowable(width="100%", thickness=1, color=border_slate))
    elements.append(Spacer(1, 0.3 * inch))

    # Student Info Grid
    info_data = [
        [Paragraph("STUDENT NAME", label_style), Paragraph("ACCOUNT EMAIL", label_style)],
        [Paragraph(request.user.full_name, value_style), Paragraph(request.user.email, value_style)],
        [Paragraph("REPORT DATE", label_style), Paragraph("CURRENT WALLET STATUS", label_style)],
        [Paragraph(datetime.now().strftime('%d %B %Y'), value_style), Paragraph(f"Active", value_style)],
    ]
    info_table = Table(info_data, colWidths=[3 * inch, 3 * inch])
    info_table.setStyle(TableStyle([('BOTTOMPADDING', (0,0), (-1,-1), 10)]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.4 * inch))

    # 6. Summary Cards (Table based)
    summary_data = [
        ["Wallet Balance", "Total Credits", "Total Debits"],
        [f"Rs. {wallet.balance:,.2f}", f"Rs. {total_credit:,.2f}", f"Rs. {total_debit:,.2f}"]
    ]
    summary_table = Table(summary_data, colWidths=[2 * inch, 2 * inch, 2 * inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#64748b")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 1), (-1, 1), 14),
        ('TEXTCOLOR', (0, 1), (0, 1), primary_indigo),
        ('TEXTCOLOR', (1, 1), (1, 1), success_emerald),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 15),
        ('TOPPADDING', (0, 1), (-1, 1), 10),
        ('BOX', (0, 0), (-1, -1), 0.5, border_slate),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5 * inch))

    # 7. Fee Ledger Table
    elements.append(Paragraph("HOSTEL FEE LEDGER", label_style))
    elements.append(Spacer(1, 0.1 * inch))
    
    ledger_data = [
        ["DESCRIPTION", "STATUS", "AMOUNT"],
        ["Hostel Fees Successfully Settled", "PAID", f"Rs. {total_fees_paid:,.2f}"],
        ["Hostel Fees Currently Owed", "PENDING", f"Rs. {total_fees_pending:,.2f}"],
    ]
    
    ledger_table = Table(ledger_data, colWidths=[3.5 * inch, 1 * inch, 1.5 * inch], rowHeights=30)
    ledger_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_indigo),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_slate),
        ('TEXTCOLOR', (1, 2), (1, 2), warning_amber), # Pending color
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(ledger_table)

    # 8. Footer
    elements.append(Spacer(1, 1 * inch))
    disclaimer = "Thank you for using Apex Hostel. This is an official statement generated for your personal records."
    elements.append(Paragraph(disclaimer, styles["Italic"]))

    # Final build
    doc.build(elements)
    return response

  


def admin_financial_dashboard(request):

    # Time filter
    filter_type = request.GET.get("filter", "month")

    now = timezone.now()

    if filter_type == "month":
        start_date = now.replace(day=1)
    elif filter_type == "year":
        start_date = now.replace(month=1, day=1)
    elif filter_type == "30days":
        start_date = now - timedelta(days=30)
    else:
        start_date = None

    # Wallet Transactions
    transactions = WalletTransaction.objects.all()

    if start_date:
        transactions = transactions.filter(created_at__gte=start_date)

    total_credit = transactions.filter(
        transaction_type="CREDIT"
    ).aggregate(Sum("amount"))["amount__sum"] or 0

    total_debit = transactions.filter(
        transaction_type="DEBIT"
    ).aggregate(Sum("amount"))["amount__sum"] or 0

    # Fees
    fees = Fee.objects.all()

    if start_date:
        fees = fees.filter(created_at__gte=start_date)

    total_fees_paid = fees.filter(status="Paid").aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    total_fees_pending = fees.filter(status="Pending").aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    total_students = User.objects.filter(role="STUDENT").count()

    context = {
        "total_credit": total_credit,
        "total_debit": total_debit,
        "total_fees_paid": total_fees_paid,
        "total_fees_pending": total_fees_pending,
        "total_students": total_students,
        "filter_type": filter_type,
    }

    return render(request, "accounts/admin_financial_dashboard.html", context)


def download_admin_financial_pdf(request):
    # 1. Setup Filter Logic
    filter_type = request.GET.get("filter", "month")
    now = timezone.now()

    if filter_type == "month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0)
    elif filter_type == "year":
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0)
    elif filter_type == "30days":
        start_date = now - timedelta(days=30)
    else:
        start_date = None

    # 2. Database Queries
    transactions = WalletTransaction.objects.all()
    fees = Fee.objects.all()

    if start_date:
        transactions = transactions.filter(created_at__gte=start_date)
        fees = fees.filter(created_at__gte=start_date)

    total_credit = transactions.filter(transaction_type="CREDIT").aggregate(Sum("amount"))["amount__sum"] or 0
    total_debit = transactions.filter(transaction_type="DEBIT").aggregate(Sum("amount"))["amount__sum"] or 0
    total_fees_paid = fees.filter(status="Paid").aggregate(Sum("amount"))["amount__sum"] or 0
    total_fees_pending = fees.filter(status="Pending").aggregate(Sum("amount"))["amount__sum"] or 0
    total_students = User.objects.filter(role="STUDENT").count()

    # 3. Setup Response & Document
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Apex_Financial_Report_{filter_type}.pdf"'

    doc = SimpleDocTemplate(
        response, 
        pagesize=A4, 
        rightMargin=40, 
        leftMargin=40, 
        topMargin=40, 
        bottomMargin=30
    )
    elements = []

    # 4. Define Colors & Styles (Using CORRECT HexColor)
    brand_indigo = colors.HexColor("#4f46e5")
    border_slate = colors.HexColor("#e2e8f0")
    zebra_bg = colors.HexColor("#f8fafc")
    text_dark = colors.HexColor("#1e293b")

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=brand_indigo,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    sub_style = ParagraphStyle(
        'SubStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=20
    )

    # 5. Build PDF Header
    elements.append(Paragraph("APEX HOSTEL", title_style))
    elements.append(Paragraph(f"ADMIN FINANCIAL AUDIT • {filter_type.upper()} OVERVIEW", sub_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=border_slate, spaceAfter=20))

    # Meta Info Table
    meta_data = [[
        f"Generated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
        f"Filter Applied: {filter_type.title()}"
    ]]
    meta_table = Table(meta_data, colWidths=[3.5 * inch, 2.5 * inch])
    meta_table.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.grey),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 0.4 * inch))

    # 6. Main Data Table
    table_data = [
        ["METRIC DESCRIPTION", "VALUE / AMOUNT"],
        ["Total Student Accounts", f"{total_students}"],
        ["Wallet Credits (Recharges)", f"Rs. {total_credit:,.2f}"],
        ["Wallet Debits (Usage)", f"Rs. {total_debit:,.2f}"],
        ["Fees Collected", f"Rs. {total_fees_paid:,.2f}"],
        ["Pending / Outstanding Fees", f"Rs. {total_fees_pending:,.2f}"],
    ]

    main_table = Table(table_data, colWidths=[3.8 * inch, 1.8 * inch], rowHeights=32)
    
    main_table.setStyle(TableStyle([
        # Header Styling
        ('BACKGROUND', (0, 0), (-1, 0), brand_indigo),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        
        # Grid & Body
        ('GRID', (0, 0), (-1, -1), 0.5, border_slate),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        
        # Zebra Stripes
        ('BACKGROUND', (0, 2), (-1, 2), zebra_bg),
        ('BACKGROUND', (0, 4), (-1, 4), zebra_bg),
        
        # Alignment
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        
        # Specific Coloring for Pending
        ('TEXTCOLOR', (1, 5), (1, 5), colors.red),
    ]))

    elements.append(main_table)

    # 7. Summary Footer
    elements.append(Spacer(1, 0.6 * inch))
    total_revenue = total_fees_paid + total_credit
    
    summary_style = ParagraphStyle(
        'Summary',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica-Bold',
        textColor=text_dark,
        alignment=2 # Right Aligned
    )
    
    elements.append(Paragraph(f"Estimated Total Revenue: Rs. {total_revenue:,.2f}", summary_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(HRFlowable(width="40%", thickness=1, color=border_slate, hAlign='RIGHT'))
    
    # Final Disclaimer
    disclaimer = ParagraphStyle('Disc', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
    elements.append(Spacer(1, 1 * inch))
    elements.append(Paragraph("This is a computer-generated document and does not require a physical signature.", disclaimer))

    # Build PDF
    doc.build(elements)
    return response