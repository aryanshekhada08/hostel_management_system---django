from django import forms
from .models import Admission

class AdmissionForm(forms.ModelForm):

    class Meta:
        model = Admission
        exclude = ('student', 'status', 'submitted_at')

        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }
