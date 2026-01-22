from django.contrib import admin
from .models import Admission

@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'year', 'status', 'submitted_at')
    list_filter = ('status', 'course')
    search_fields = ('student__full_name', 'student__email')
