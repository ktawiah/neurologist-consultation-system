from django import forms
from ..models import VitalSign, LabResult, ImagingStudy, NeurologistConsultation

class VitalSignForm(forms.ModelForm):
    class Meta:
        model = VitalSign
        fields = [
            'blood_pressure_systolic', 'blood_pressure_diastolic',
            'heart_rate', 'respiratory_rate', 'oxygen_saturation'
        ]
        widgets = {
            'blood_pressure_systolic': forms.NumberInput(attrs={'min': 0}),
            'blood_pressure_diastolic': forms.NumberInput(attrs={'min': 0}),
            'heart_rate': forms.NumberInput(attrs={'min': 0}),
            'respiratory_rate': forms.NumberInput(attrs={'min': 0}),
            'oxygen_saturation': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        }

class LabResultForm(forms.ModelForm):
    class Meta:
        model = LabResult
        fields = [
            'cbc', 'bmp', 'coagulation_studies',
            'glucose', 'creatinine'
        ]
        widgets = {
            'cbc': forms.Textarea(attrs={'rows': 3}),
            'bmp': forms.Textarea(attrs={'rows': 3}),
            'coagulation_studies': forms.Textarea(attrs={'rows': 3}),
            'glucose': forms.NumberInput(attrs={'step': '0.01'}),
            'creatinine': forms.NumberInput(attrs={'step': '0.01'}),
        }

class ImagingStudyForm(forms.ModelForm):
    class Meta:
        model = ImagingStudy
        fields = ['study_type', 'findings']
        widgets = {
            'findings': forms.Textarea(attrs={'rows': 5}),
        }

class ConsultationForm(forms.ModelForm):
    class Meta:
        model = NeurologistConsultation
        fields = ['diagnosis', 'treatment_plan', 'additional_tests']
        widgets = {
            'diagnosis': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter diagnosis'
            }),
            'treatment_plan': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter detailed treatment plan and recommendations'
            }),
            'additional_tests': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter any additional tests or studies needed'
            })
        }
        labels = {
            'diagnosis': 'Diagnosis',
            'treatment_plan': 'Treatment Plan',
            'additional_tests': 'Additional Tests/Studies'
        }
        help_texts = {
            'diagnosis': 'Specify the primary diagnosis based on your assessment',
            'treatment_plan': 'Detail the recommended treatment plan including medications and interventions',
            'additional_tests': 'List any additional tests or studies that should be performed'
        }
