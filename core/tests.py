from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Patient, VitalSign, LabResult, ImagingStudy, NeurologistConsultation
from datetime import date, timedelta

User = get_user_model()

class ModelTests(TestCase):
    def setUp(self):
        self.technician = User.objects.create_user(
            username='test_tech',
            password='testpass123',
            role=User.Role.MOBILE_TECHNICIAN
        )
        self.neurologist = User.objects.create_user(
            username='test_neuro',
            password='testpass123',
            role=User.Role.NEUROLOGIST
        )

    def test_create_patient(self):
        patient = Patient.objects.create(
            first_name='Test',
            last_name='Patient',
            date_of_birth=date(1990, 1, 1),
            sex='M',
            medical_history='None',
            chief_complaint='Test complaint',
            nihss_score=5,
            created_by=self.technician
        )
        self.assertEqual(str(patient), 'Test Patient')

    def test_create_vital_signs(self):
        patient = Patient.objects.create(
            first_name='Test',
            last_name='Patient',
            date_of_birth=date(1990, 1, 1),
            sex='M',
            medical_history='None',
            chief_complaint='Test complaint',
            nihss_score=5,
            created_by=self.technician
        )
        vital_sign = VitalSign.objects.create(
            patient=patient,
            blood_pressure_systolic=120,
            blood_pressure_diastolic=80,
            heart_rate=70,
            respiratory_rate=16,
            oxygen_saturation=98,
            recorded_by=self.technician
        )
        self.assertEqual(vital_sign.patient, patient)

class APITests(APITestCase):
    def setUp(self):
        self.technician = User.objects.create_user(
            username='test_tech',
            password='testpass123',
            role=User.Role.MOBILE_TECHNICIAN
        )
        self.neurologist = User.objects.create_user(
            username='test_neuro',
            password='testpass123',
            role=User.Role.NEUROLOGIST
        )
        self.client = APIClient()

    def test_patient_list_unauthorized(self):
        url = reverse('patient-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patient_list_authorized(self):
        self.client.force_authenticate(user=self.technician)
        url = reverse('patient-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_patient(self):
        self.client.force_authenticate(user=self.technician)
        url = reverse('patient-list')
        data = {
            'first_name': 'Test',
            'last_name': 'Patient',
            'date_of_birth': '1990-01-01',
            'sex': 'M',
            'medical_history': 'None',
            'chief_complaint': 'Test complaint',
            'nihss_score': 5
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.count(), 1)
        self.assertEqual(Patient.objects.get().first_name, 'Test')

    def test_consultation_permissions(self):
        # Create a patient
        patient = Patient.objects.create(
            first_name='Test',
            last_name='Patient',
            date_of_birth=date(1990, 1, 1),
            sex='M',
            medical_history='None',
            chief_complaint='Test complaint',
            nihss_score=5,
            created_by=self.technician
        )

        # Try to create consultation as technician (should fail)
        self.client.force_authenticate(user=self.technician)
        url = reverse('neurologistconsultation-list')
        data = {
            'patient': patient.id,
            'diagnosis': 'Test diagnosis',
            'treatment_plan': 'Test treatment'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Try to create consultation as neurologist (should succeed)
        self.client.force_authenticate(user=self.neurologist)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
