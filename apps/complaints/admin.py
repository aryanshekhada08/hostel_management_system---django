from django.contrib import admin
from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'room_number', 'category', 'status', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'student__email')