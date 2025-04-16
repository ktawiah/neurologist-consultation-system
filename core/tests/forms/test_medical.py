from django.test import TestCase
from django.core.exceptions import ValidationError
from core.forms.medical import VitalSignForm, LabResultForm, ImagingStudyForm
from core.models.user import User
from core.models.patient import Patient
from core.models.medical import VitalSign, LabResult, ImagingStudy

class MedicalFormsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.patient = Patient.objects.create(
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            sex=Patient.Sex.MALE,
            medical_history='No significant medical history',
            chief_complaint='Headache and dizziness',
            nihss_score=5,
            created_by=self.user
        )

    def test_vital_sign_form_valid(self):
        """Test that the vital sign form works with valid data"""
        vital_sign_data = {
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'heart_rate': 75,
            'respiratory_rate': 16,
            'oxygen_saturation': 98
        }
        form = VitalSignForm(data=vital_sign_data)
        self.assertTrue(form.is_valid())
        vital_sign = form.save(commit=False)
        vital_sign.patient = self.patient
        vital_sign.recorded_by = self.user
        vital_sign.save()
        self.assertEqual(vital_sign.blood_pressure_systolic, vital_sign_data['blood_pressure_systolic'])
        self.assertEqual(vital_sign.blood_pressure_diastolic, vital_sign_data['blood_pressure_diastolic'])
        self.assertEqual(vital_sign.heart_rate, vital_sign_data['heart_rate'])
        self.assertEqual(vital_sign.respiratory_rate, vital_sign_data['respiratory_rate'])
        self.assertEqual(vital_sign.oxygen_saturation, vital_sign_data['oxygen_saturation'])

    def test_vital_sign_form_validation(self):
        """Test vital sign form validation"""
        # Test with invalid blood pressure
        data = {
            'blood_pressure_systolic': 50,  # Too low
            'blood_pressure_diastolic': 30,  # Too low
            'heart_rate': 75,
            'respiratory_rate': 16,
            'oxygen_saturation': 98
        }
        form = VitalSignForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('blood_pressure_systolic', form.errors)
        self.assertIn('blood_pressure_diastolic', form.errors)

        # Test with invalid oxygen saturation
        data['blood_pressure_systolic'] = 120
        data['blood_pressure_diastolic'] = 80
        data['oxygen_saturation'] = 50  # Too low
        form = VitalSignForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('oxygen_saturation', form.errors)

    def test_lab_result_form_valid(self):
        """Test that the lab result form works with valid data"""
        lab_result_data = {
            'cbc': 'Normal',
            'bmp': 'Normal',
            'coagulation_studies': 'Normal',
            'glucose': 95.5,
            'creatinine': 0.8
        }
        form = LabResultForm(data=lab_result_data)
        self.assertTrue(form.is_valid())
        lab_result = form.save(commit=False)
        lab_result.patient = self.patient
        lab_result.recorded_by = self.user
        lab_result.save()
        self.assertEqual(lab_result.cbc, lab_result_data['cbc'])
        self.assertEqual(lab_result.bmp, lab_result_data['bmp'])
        self.assertEqual(lab_result.coagulation_studies, lab_result_data['coagulation_studies'])
        self.assertEqual(lab_result.glucose, lab_result_data['glucose'])
        self.assertEqual(lab_result.creatinine, lab_result_data['creatinine'])

    def test_lab_result_form_validation(self):
        """Test lab result form validation"""
        # Test with invalid glucose level
        data = {
            'cbc': 'Normal',
            'bmp': 'Normal',
            'coagulation_studies': 'Normal',
            'glucose': 1000,  # Too high
            'creatinine': 0.8
        }
        form = LabResultForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('glucose', form.errors)

        # Test with invalid creatinine level
        data['glucose'] = 95.5
        data['creatinine'] = -0.5  # Invalid
        form = LabResultForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('creatinine', form.errors)

    def test_imaging_study_form_valid(self):
        """Test that the imaging study form works with valid data"""
        imaging_study_data = {
            'study_type': ImagingStudy.StudyType.CT,
            'findings': 'No acute findings'
        }
        form = ImagingStudyForm(data=imaging_study_data)
        self.assertTrue(form.is_valid())
        imaging_study = form.save(commit=False)
        imaging_study.patient = self.patient
        imaging_study.recorded_by = self.user
        imaging_study.save()
        self.assertEqual(imaging_study.study_type, imaging_study_data['study_type'])
        self.assertEqual(imaging_study.findings, imaging_study_data['findings'])

    def test_imaging_study_form_validation(self):
        """Test imaging study form validation"""
        # Test with missing required fields
        data = {
            'study_type': ImagingStudy.StudyType.CT
            # Missing findings
        }
        form = ImagingStudyForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('findings', form.errors)

        # Test with invalid study type
        data['findings'] = 'No acute findings'
        data['study_type'] = 'INVALID'  # Invalid study type
        form = ImagingStudyForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('study_type', form.errors) 