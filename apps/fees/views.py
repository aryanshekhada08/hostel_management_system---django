from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth import get_user_model
from .models import Fee, Payment

User = get_user_model()


# ===========================
# ADMIN - FEE DASHBOARD
# ===========================

@login_required
def fee_dashboard(request):

    if request.user.role != "ADMIN":
        return redirect("home")

    search_query = request.GET.get("search", "").strip()

    fees = Fee.objects.select_related("student").order_by("-created_at")

    if search_query:
        fees = fees.filter(
            Q(student__email__icontains=search_query) |
            Q(student__full_name__icontains=search_query)
        )

    # 🔥 Auto Update Status
    # for fee in fees:
    #     fee.update_status()

    # return render(request, "fees/fee_dashboard.html", {
    #     "fees": fees,
    #     "search_query": search_query,
    # })


# ===========================
# ADMIN - ADD FEE
# ===========================

@login_required
def add_fee(request):

    if request.user.role != "ADMIN":
        return redirect("home")

    students = User.objects.filter(role="STUDENT")

    if request.method == "POST":
        student_id = request.POST.get("student")
        amount = request.POST.get("amount")
        due_date = request.POST.get("due_date")

        Fee.objects.create(
            student_id=student_id,
            amount=amount,
            due_date=due_date
        )

        messages.success(request, "Fee assigned successfully!")
        return redirect("fee_dashboard")

    return render(request, "fees/add_fee.html", {
        "students": students
    })


# ===========================
# ADMIN - EDIT FEE
# ===========================

@login_required
def edit_fee(request, fee_id):

    if request.user.role != "ADMIN":
        return redirect("home")

    fee = get_object_or_404(Fee, id=fee_id)

    if request.method == "POST":
        fee.paid_amount = Decimal(request.POST.get("paid_amount") or 0)
        fee.save()
        fee.update_status()

        messages.success(request, "Fee updated successfully!")
        return redirect("fee_dashboard")

    return render(request, "fees/edit_fee.html", {
        "fee": fee
    })


# ===========================
# ADMIN - DELETE FEE
# ===========================

@login_required
def delete_fee(request, fee_id):

    if request.user.role != "ADMIN":
        return redirect("home")

    fee = get_object_or_404(Fee, id=fee_id)
    fee.delete()

    messages.success(request, "Fee deleted successfully!")
    return redirect("fee_dashboard")


# ===========================
# STUDENT - PAY FEE
# ===========================

@login_required
def pay_fee(request, fee_id):

    fee = get_object_or_404(Fee, id=fee_id, student=request.user)

    payment_amount = 1000  # simulate payment

    # Create payment record
    Payment.objects.create(
        student=request.user,
        fee=fee,
        amount=payment_amount,
        payment_method="Online"
    )

    # Update fee amount
    fee.paid_amount += payment_amount
    fee.save()
    fee.update_status()

    messages.success(request, f"₹{payment_amount} Payment Successful!")

    return redirect("accounts:student_dashboard")


# ===========================
# STUDENT - FEE HISTORY
# ===========================

@login_required
def student_fee_history(request):

    if request.user.role != "STUDENT":
        return redirect("home")

    fees = Fee.objects.filter(
        student=request.user
    ).order_by("-created_at")

    for fee in fees:
        fee.update_status()

    return render(request, "fees/student_fee_history.html", {
        "fees": fees
    })


# ===========================
# STUDENT - PAYMENT HISTORY
# ===========================

@login_required
def payment_history(request):

    payments = Payment.objects.filter(
        student=request.user
    ).select_related("fee").order_by("-payment_date")

    return render(request, "fees/payment_history.html", {
        "payments": payments
    })

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
import io
import os
import qrcode

@login_required
def download_receipt(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)

    buffer = io.BytesIO()
    # Set tight margins to maximize space
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    
    # Custom CSS-like Styles
    styles = getSampleStyleSheet()
    brand_color = colors.HexColor("#2C3E50") # Professional Dark Navy
    accent_color = colors.HexColor("#3498DB") # Soft Blue
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, textColor=brand_color, spaceAfter=2)
    label_style = ParagraphStyle('LabelStyle', parent=styles['Normal'], fontSize=9, textColor=colors.grey, leading=12)
    value_style = ParagraphStyle('ValueStyle', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', leading=14)

    # =====================
    # HEADER (Logo Left, Title Right)
    # =====================
    logo_path = os.path.join(settings.BASE_DIR, "static/images/logo.png")
    logo_img = ""
    if os.path.exists(logo_path):
        logo_img = Image(logo_path, width=1.2 * inch, height=1.2 * inch)

    header_content = [
        [logo_img, [Paragraph("<b>HOSTEL MANAGEMENT</b>", title_style), 
                   Paragraph("Official Payment Receipt", styles['Normal']),
                   Paragraph(f"Receipt ID: {payment.transaction_id}", label_style)]]
    ]
    header_table = Table(header_content, colWidths=[1.5 * inch, 4 * inch])
    header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(header_table)
    
    # Blue Accent Line
    elements.append(Spacer(1, 10))
    elements.append(Table([[""]], colWidths=[5.5*inch], rowHeights=[2], style=[('BACKGROUND', (0,0), (-1,-1), accent_color)]))
    elements.append(Spacer(1, 20))

    # =====================
    # INFO SECTION (Two Columns)
    # =====================
    info_data = [
        [Paragraph("BILLED TO", label_style), Paragraph("PAYMENT DATE", label_style)],
        [Paragraph(payment.student.full_name, value_style), Paragraph(payment.payment_date.strftime("%d %b %Y"), value_style)],
        [Paragraph(payment.student.email, styles['Normal']), Paragraph(payment.payment_date.strftime("%H:%M %p"), styles['Normal'])]
    ]
    info_table = Table(info_data, colWidths=[3 * inch, 2.5 * inch])
    elements.append(info_table)
    elements.append(Spacer(1, 25))

    # =====================
    # TABLE DATA (The "CSS" Part)
    # =====================
    # Modern look: Header has background, rows have thin line below
    table_header = [["Description", "Method", "Status", "Amount"]]
    table_rows = [
        ["Hostel Monthly/Security Fee", payment.payment_method, payment.fee.status.upper(), f"INR {payment.amount}"]
    ]
    
    main_table = Table(table_header + table_rows, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch])
    main_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), brand_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'), # Amount column to right
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.lightgrey), # Subtle row line
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.whitesmoke]) # Zebra stripes
    ]))
    elements.append(main_table)
    elements.append(Spacer(1, 20))

    # =====================
    # QR CODE & TOTAL (Side by Side)
    # =====================
    qr_data = f"ID:{payment.transaction_id} | Name:{payment.student.full_name} | Amt:{payment.amount}"
    qr = qrcode.make(qr_data)
    qr_buffer = io.BytesIO()
    qr.save(qr_buffer)
    qr_buffer.seek(0)
    qr_image = Image(qr_buffer, width=1.2 * inch, height=1.2 * inch)

    # Placing QR on left and Total Amount on right
    footer_summary = [
        [qr_image, "", [Paragraph("GRAND TOTAL", label_style), 
                       Paragraph(f"₹{payment.amount}", ParagraphStyle('Total', fontSize=18, fontName='Helvetica-Bold'))]]
    ]
    summary_table = Table(footer_summary, colWidths=[1.5*inch, 2*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT')
    ]))
    elements.append(summary_table)

    # =====================
    # SIGNATURE & FOOTER
    # =====================
    elements.append(Spacer(1, 40))
    footer_note = Paragraph("<i>This is a computer-generated receipt. No physical signature required.</i>", label_style)
    elements.append(footer_note)

    # Build PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.transaction_id}.pdf"'
    return response