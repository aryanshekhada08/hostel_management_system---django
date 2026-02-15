from django.db import models
from django.conf import settings
from django.utils import timezone

from django.utils import timezone
import uuid


class Fee(models.Model):

    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Partial", "Partial"),
        ("Overdue", "Overdue"),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="fees"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")

    created_at = models.DateTimeField(auto_now_add=True)

    # 🔥 Remaining amount
    def remaining_amount(self):
        return self.amount - self.paid_amount

    # 🔥 Auto update status


    def update_status(self):
            today = timezone.now().date()

            if self.paid_amount >= self.amount:
                self.status = "Paid"
            elif self.due_date < today:
                self.status = "Overdue"
            elif self.paid_amount > 0:
                self.status = "Partial"
            else:
                self.status = "Pending"

            super().save()

    def __str__(self):
        return f"{self.student.full_name} - ₹{self.amount} ({self.status})"



class Payment(models.Model):

    PAYMENT_METHODS = (
        ("Cash", "Cash"),
        ("Online", "Online"),
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    fee = models.ForeignKey(
        "Fee",
        on_delete=models.CASCADE,
        related_name="payments"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default="Cash"
    )

    transaction_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    payment_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.full_name} - ₹{self.amount}"