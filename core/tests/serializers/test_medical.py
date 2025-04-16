from django.test import TestCase, RequestFactory
from django.utils import timezone
from core.models.user import User
from core.models.patient import Patient
from core.models.medical import VitalSign, LabResult, ImagingStudy
from core.serializers.medical import VitalSignSerializer, LabResultSerializer, ImagingStudySerializer

class MedicalSerializersTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
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
        self.request = self.factory.get('/')
        self.request.user = self.user

    def test_vital_sign_serializer(self):
        """Test VitalSign serializer"""
        vital_sign_data = {
            'patient': self.patient.id,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'heart_rate': 75,
            'respiratory_rate': 16,
            'oxygen_saturation': 98,
            'recorded_by': self.user.id
        }

        # Test serialization
        vital_sign = VitalSign.objects.create(
            patient=self.patient,
            blood_pressure_systolic=120,
            blood_pressure_diastolic=80,
            heart_rate=75,
            respiratory_rate=16,
            oxygen_saturation=98,
            recorded_by=self.user
        )
        serializer = VitalSignSerializer(vital_sign)
        data = serializer.data
        self.assertEqual(data['blood_pressure_systolic'], vital_sign_data['blood_pressure_systolic'])
        self.assertEqual(data['blood_pressure_diastolic'], vital_sign_data['blood_pressure_diastolic'])
        self.assertEqual(data['heart_rate'], vital_sign_data['heart_rate'])
        self.assertEqual(data['respiratory_rate'], vital_sign_data['respiratory_rate'])
        self.assertEqual(data['oxygen_saturation'], vital_sign_data['oxygen_saturation'])

        # Test deserialization
        serializer = VitalSignSerializer(data=vital_sign_data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        vital_sign = serializer.save()
        self.assertEqual(vital_sign.patient, self.patient)
        self.assertEqual(vital_sign.recorded_by, self.user)

    def test_lab_result_serializer(self):
        """Test LabResult serializer"""
        lab_result_data = {
            'patient': self.patient.id,
            'cbc': 'Normal',
            'bmp': 'Normal',
            'coagulation_studies': 'Normal',
            'glucose': 95.5,
            'creatinine': 0.8,
            'recorded_by': self.user.id
        }

        # Test serialization
        lab_result = LabResult.objects.create(
            patient=self.patient,
            cbc='Normal',
            bmp='Normal',
            coagulation_studies='Normal',
            glucose=95.5,
            creatinine=0.8,
            recorded_by=self.user
        )
        serializer = LabResultSerializer(lab_result)
        data = serializer.data
        self.assertEqual(data['cbc'], lab_result_data['cbc'])
        self.assertEqual(data['bmp'], lab_result_data['bmp'])
        self.assertEqual(data['coagulation_studies'], lab_result_data['coagulation_studies'])
        self.assertEqual(float(data['glucose']), lab_result_data['glucose'])
        self.assertEqual(float(data['creatinine']), lab_result_data['creatinine'])

        # Test deserialization
        serializer = LabResultSerializer(data=lab_result_data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        lab_result = serializer.save()
        self.assertEqual(lab_result.patient, self.patient)
        self.assertEqual(lab_result.recorded_by, self.user)

    def test_imaging_study_serializer(self):
        """Test ImagingStudy serializer"""
        imaging_study_data = {
            'patient': self.patient.id,
            'study_type': ImagingStudy.StudyType.CT,
            'findings': 'No acute findings',
            'recorded_by': self.user.id
        }

        # Test serialization
        imaging_study = ImagingStudy.objects.create(
            patient=self.patient,
            study_type=ImagingStudy.StudyType.CT,
            findings='No acute findings',
            recorded_by=self.user
        )
        serializer = ImagingStudySerializer(imaging_study)
        data = serializer.data
        self.assertEqual(data['study_type'], imaging_study_data['study_type'])
        self.assertEqual(data['findings'], imaging_study_data['findings'])

        # Test deserialization
        serializer = ImagingStudySerializer(data=imaging_study_data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        imaging_study = serializer.save()
        self.assertEqual(imaging_study.patient, self.patient)
        self.assertEqual(imaging_study.recorded_by, self.user)

    def test_medical_serializer_validation(self):
        """Test validation for medical serializers"""
        # Test VitalSign validation
        vital_sign_data = {
            'patient': self.patient.id,
            'blood_pressure_systolic': -50,  # Invalid: negative value
            'blood_pressure_diastolic': 80,
            'heart_rate': 75,
            'respiratory_rate': 16,
            'oxygen_saturation': 98,
            'recorded_by': self.user.id
        }
        serializer = VitalSignSerializer(data=vital_sign_data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('blood_pressure_systolic', serializer.errors)

        # Test LabResult validation
        lab_result_data = {
            'patient': self.patient.id,
            'cbc': 'Normal',
            'bmp': 'Normal',
            'coagulation_studies': 'Normal',
            'glucose': -100,  # Invalid: negative value
            'creatinine': 0.8,
            'recorded_by': self.user.id
        }
        serializer = LabResultSerializer(data=lab_result_data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('glucose', serializer.errors)

        # Test ImagingStudy validation
        imaging_study_data = {
            'patient': self.patient.id,
            'study_type': 'INVALID',  # Invalid study type
            'findings': 'No acute findings',
            'recorded_by': self.user.id
        }
        serializer = ImagingStudySerializer(data=imaging_study_data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('study_type', serializer.errors) 