from django.db import models
from django.conf import settings


class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    capacity = models.IntegerField()
    occupied = models.IntegerField(default=0)

    def __str__(self):
        return f"Room {self.room_number}"

    def is_available(self):
        return self.occupied < self.capacity


class RoomAllocation(models.Model):
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    allocated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} → {self.room.room_number}"

