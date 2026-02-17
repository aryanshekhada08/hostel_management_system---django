from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Complaint(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]

    CATEGORY_CHOICES = [
        ('Electricity', 'Electricity'),
        ('Water', 'Water'),
        ('Cleaning', 'Cleaning'),
        ('WiFi', 'WiFi'),
        ('Mess', 'Mess'),
        ('Other', 'Other'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    description = models.TextField()
    room_number = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.status}"