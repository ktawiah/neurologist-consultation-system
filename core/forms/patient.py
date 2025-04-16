from django import forms
from ..models import Patient

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'sex',
            'medical_history', 'chief_complaint', 'nihss_score'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'medical_history': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter relevant medical history'
            }),
            'chief_complaint': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter the main reason for consultation'
            }),
            'nihss_score': forms.NumberInput(attrs={
                'min': 0,
                'max': 42,
                'placeholder': 'Enter NIHSS score (0-42)'
            })
        }
        help_texts = {
            'nihss_score': 'National Institutes of Health Stroke Scale score (0-42)',
            'medical_history': 'Include relevant past medical conditions, medications, and risk factors',
            'chief_complaint': 'Describe the main symptoms or reasons for seeking medical attention'
        }
