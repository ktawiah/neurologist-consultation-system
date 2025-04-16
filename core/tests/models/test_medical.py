from django.test import TestCase
from django.utils import timezone
from core.models.user import User
from core.models.patient import Patient
from core.models.medical import VitalSign, LabResult, ImagingStudy

class MedicalModelsTest(TestCase):
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

    def test_vital_sign_creation(self):
        """Test creating vital signs"""
        vital_sign = VitalSign.objects.create(
            patient=self.patient,
            blood_pressure_systolic=120,
            blood_pressure_diastolic=80,
            heart_rate=75,
            respiratory_rate=16,
            oxygen_saturation=98,
            recorded_by=self.user
        )
        self.assertEqual(vital_sign.patient, self.patient)
        self.assertEqual(vital_sign.blood_pressure_systolic, 120)
        self.assertEqual(vital_sign.blood_pressure_diastolic, 80)
        self.assertEqual(vital_sign.heart_rate, 75)
        self.assertEqual(vital_sign.respiratory_rate, 16)
        self.assertEqual(vital_sign.oxygen_saturation, 98)
        self.assertEqual(vital_sign.recorded_by, self.user)

    def test_vital_sign_str_representation(self):
        """Test the string representation of vital signs"""
        vital_sign = VitalSign.objects.create(
            patient=self.patient,
            blood_pressure_systolic=120,
            blood_pressure_diastolic=80,
            heart_rate=75,
            respiratory_rate=16,
            oxygen_saturation=98,
            recorded_by=self.user
        )
        self.assertEqual(str(vital_sign), f"Vitals for {self.patient} at {vital_sign.recorded_at}")

    def test_lab_result_creation(self):
        """Test creating lab results"""
        lab_result = LabResult.objects.create(
            patient=self.patient,
            cbc='Normal',
            bmp='Normal',
            coagulation_studies='Normal',
            glucose=95.5,
            creatinine=0.8,
            recorded_by=self.user
        )
        self.assertEqual(lab_result.patient, self.patient)
        self.assertEqual(lab_result.cbc, 'Normal')
        self.assertEqual(lab_result.bmp, 'Normal')
        self.assertEqual(lab_result.coagulation_studies, 'Normal')
        self.assertEqual(lab_result.glucose, 95.5)
        self.assertEqual(lab_result.creatinine, 0.8)
        self.assertEqual(lab_result.recorded_by, self.user)

    def test_imaging_study_creation(self):
        """Test creating imaging studies"""
        imaging_study = ImagingStudy.objects.create(
            patient=self.patient,
            study_type=ImagingStudy.StudyType.CT,
            findings='No acute findings',
            recorded_by=self.user
        )
        self.assertEqual(imaging_study.patient, self.patient)
        self.assertEqual(imaging_study.study_type, ImagingStudy.StudyType.CT)
        self.assertEqual(imaging_study.findings, 'No acute findings')
        self.assertEqual(imaging_study.recorded_by, self.user)

    def test_imaging_study_str_representation(self):
        """Test the string representation of imaging studies"""
        imaging_study = ImagingStudy.objects.create(
            patient=self.patient,
            study_type=ImagingStudy.StudyType.CT,
            findings='No acute findings',
            recorded_by=self.user
        )
        self.assertEqual(str(imaging_study), f"{imaging_study.study_type} for {self.patient}")

    def test_imaging_study_choices(self):
        """Test that study type choices are correctly defined"""
        choices = ImagingStudy.StudyType.choices
        self.assertEqual(len(choices), 2)
        self.assertIn(('CT', 'CT Scan'), choices)
        self.assertIn(('MRI', 'MRI'), choices)

    def test_vital_sign_alert_creation(self):
        """Test that critical vital signs create alerts"""
        vital_sign = VitalSign.objects.create(
            patient=self.patient,
            blood_pressure_systolic=190,
            blood_pressure_diastolic=110,
            heart_rate=130,
            respiratory_rate=16,
            oxygen_saturation=85,
            recorded_by=self.user
        )
        self.assertTrue(self.patient.has_critical_alerts) 