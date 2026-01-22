from django.db import models
from django.conf import settings

class Admission(models.Model):

    STATUS_CHOICES = (
        ('SUBMITTED', 'Submitted'),
        ('UNDER_REVIEW', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('WAITLISTED', 'Waitlisted'),
    )

    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'STUDENT'}
    )

    # Personal details
    dob = models.DateField()
    gender = models.CharField(max_length=10)

    # Academic details
    course = models.CharField(max_length=100)
    year = models.PositiveIntegerField()

    # Guardian & contact
    guardian_name = models.CharField(max_length=255)
    guardian_phone = models.CharField(max_length=15)
    address = models.TextField()

    # Documents
    document = models.FileField(upload_to='admissions/documents/')

    # Declaration
    declaration = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SUBMITTED'
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.status}"
