from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from core.models.user import User
from core.models.patient import Patient

class PatientModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.patient_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': date(1990, 1, 1),
            'sex': Patient.Sex.MALE,
            'medical_history': 'No significant medical history',
            'chief_complaint': 'Headache and dizziness',
            'nihss_score': 5,
            'created_by': self.user
        }

    def test_create_patient(self):
        """Test creating a new patient"""
        patient = Patient.objects.create(**self.patient_data)
        self.assertEqual(patient.first_name, self.patient_data['first_name'])
        self.assertEqual(patient.last_name, self.patient_data['last_name'])
        self.assertEqual(patient.date_of_birth, self.patient_data['date_of_birth'])
        self.assertEqual(patient.sex, self.patient_data['sex'])
        self.assertEqual(patient.medical_history, self.patient_data['medical_history'])
        self.assertEqual(patient.chief_complaint, self.patient_data['chief_complaint'])
        self.assertEqual(patient.nihss_score, self.patient_data['nihss_score'])
        self.assertEqual(patient.created_by, self.patient_data['created_by'])

    def test_patient_str_representation(self):
        """Test the string representation of a patient"""
        patient = Patient.objects.create(**self.patient_data)
        self.assertEqual(str(patient), f"{patient.first_name} {patient.last_name}")

    def test_patient_age_calculation(self):
        """Test the age property calculation"""
        patient = Patient.objects.create(**self.patient_data)
        expected_age = date.today().year - self.patient_data['date_of_birth'].year
        self.assertEqual(patient.age, expected_age)

    def test_has_critical_alerts(self):
        """Test the has_critical_alerts property"""
        patient = Patient.objects.create(**self.patient_data)
        self.assertFalse(patient.has_critical_alerts)

    def test_has_pending_consultation(self):
        """Test the has_pending_consultation property"""
        patient = Patient.objects.create(**self.patient_data)
        self.assertTrue(patient.has_pending_consultation)

    def test_sex_choices(self):
        """Test that sex choices are correctly defined"""
        choices = Patient.Sex.choices
        self.assertEqual(len(choices), 3)
        self.assertIn(('M', 'Male'), choices)
        self.assertIn(('F', 'Female'), choices)
        self.assertIn(('O', 'Other'), choices)

    def test_nihss_score_alert(self):
        """Test that high NIHSS score creates an alert"""
        patient = Patient.objects.create(**self.patient_data)
        patient.nihss_score = 15
        patient.save()
        self.assertTrue(patient.has_critical_alerts) 