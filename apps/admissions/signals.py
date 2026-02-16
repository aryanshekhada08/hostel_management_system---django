from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from .models import Admission
from apps.rooms.models import Room
from apps.wallets.models import Wallet
from apps.notifications.models import Notification


@receiver(post_save, sender=Admission)
def handle_admission_approval(sender, instance, created, **kwargs):

    # Only trigger when status becomes APPROVED
    if instance.status == 'APPROVED':

        student = instance.student

        # ✅ 1. Assign Room (First Available Room)
        available_room = Room.objects.filter(is_full=False).first()

        if available_room:
            available_room.occupied_beds += 1

            if available_room.occupied_beds >= available_room.capacity:
                available_room.is_full = True

            available_room.save()

            student.room = available_room
            student.save()

        # ✅ 2. Create Wallet (if not exists)
        Wallet.objects.get_or_create(user=student)

        # ✅ 3. Create Notification
        Notification.objects.create(
            user=student,
            title="Admission Approved 🎉",
            message="Congratulations! Your hostel admission has been approved."
        )

        # ✅ 4. Send Email
        send_mail(
            subject="Hostel Admission Approved",
            message="Your admission has been approved. Login to your dashboard for details.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.email],
            fail_silently=True,
        )