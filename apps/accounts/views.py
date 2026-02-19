from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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

    # 🔔 Unread Notifications
    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    context = {
        "room_number": room_number,
        "fee": fee,
        "unread_count": unread_count,
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
