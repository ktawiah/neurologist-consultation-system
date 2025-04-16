from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Patient, VitalSign, LabResult, ImagingStudy, NeurologistConsultation

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email required
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        # Add role choices
        self.fields['role'] = forms.ChoiceField(
            choices=User.Role.choices,
            required=True,
            help_text='Select your role in the system'
        )

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'sex',
            'medical_history', 'chief_complaint', 'nihss_score',
            'diagnosis', 'treatment', 'outcome', 'disposition', 'follow_up_plan'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'medical_history': forms.Textarea(attrs={'rows': 3}),
            'chief_complaint': forms.Textarea(attrs={'rows': 3}),
            'treatment': forms.Textarea(attrs={'rows': 3}),
            'outcome': forms.Textarea(attrs={'rows': 3}),
            'follow_up_plan': forms.Textarea(attrs={'rows': 3}),
        }

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