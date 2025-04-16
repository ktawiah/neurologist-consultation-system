from django.test import TestCase, RequestFactory
from django.utils import timezone
from core.models.user import User
from core.models.patient import Patient
from core.serializers.patient import PatientSerializer

class PatientSerializerTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.request = self.factory.get('/')
        self.request.user = self.user
        self.patient_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1990-01-01',
            'sex': Patient.Sex.MALE,
            'medical_history': 'No significant medical history',
            'chief_complaint': 'Headache and dizziness',
            'nihss_score': 5,
            'created_by': self.user.id
        }
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

    def test_patient_serializer_serialization(self):
        """Test serializing a patient"""
        serializer = PatientSerializer(self.patient, context={'request': self.request})
        data = serializer.data
        self.assertEqual(data['first_name'], self.patient_data['first_name'])
        self.assertEqual(data['last_name'], self.patient_data['last_name'])
        self.assertEqual(data['date_of_birth'], self.patient_data['date_of_birth'])
        self.assertEqual(data['sex'], self.patient_data['sex'])
        self.assertEqual(data['medical_history'], self.patient_data['medical_history'])
        self.assertEqual(data['chief_complaint'], self.patient_data['chief_complaint'])
        self.assertEqual(data['nihss_score'], self.patient_data['nihss_score'])
        self.assertEqual(data['created_by'], self.patient_data['created_by'])

    def test_patient_serializer_deserialization(self):
        """Test deserializing patient data"""
        # Create new patient data to avoid unique constraint issues
        new_patient_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'date_of_birth': '1995-01-01',
            'sex': Patient.Sex.FEMALE,
            'medical_history': 'No significant medical history',
            'chief_complaint': 'Headache',
            'nihss_score': 3,
            'created_by': self.user.id
        }
        serializer = PatientSerializer(data=new_patient_data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        patient = serializer.save()
        self.assertEqual(patient.first_name, new_patient_data['first_name'])
        self.assertEqual(patient.last_name, new_patient_data['last_name'])
        self.assertEqual(str(patient.date_of_birth), new_patient_data['date_of_birth'])
        self.assertEqual(patient.sex, new_patient_data['sex'])
        self.assertEqual(patient.medical_history, new_patient_data['medical_history'])
        self.assertEqual(patient.chief_complaint, new_patient_data['chief_complaint'])
        self.assertEqual(patient.nihss_score, new_patient_data['nihss_score'])
        self.assertEqual(patient.created_by.id, new_patient_data['created_by'])

    def test_patient_serializer_validation(self):
        """Test serializer validation"""
        # Test with missing required fields
        data = {}
        serializer = PatientSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        required_fields = ['first_name', 'last_name', 'date_of_birth', 'sex', 
                         'chief_complaint', 'nihss_score']
        for field in required_fields:
            self.assertIn(field, serializer.errors)

        # Test with invalid date format
        data = self.patient_data.copy()
        data['date_of_birth'] = 'invalid-date'
        serializer = PatientSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('date_of_birth', serializer.errors)

        # Test with invalid NIHSS score
        data = self.patient_data.copy()
        data['nihss_score'] = -1
        serializer = PatientSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('nihss_score', serializer.errors)

        # Test with invalid sex
        data = self.patient_data.copy()
        data['sex'] = 'INVALID'
        serializer = PatientSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('sex', serializer.errors)

        # Test with future date of birth
        data = self.patient_data.copy()
        data['date_of_birth'] = '2100-01-01'
        serializer = PatientSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('date_of_birth', serializer.errors)

    def test_patient_serializer_update(self):
        """Test updating a patient"""
        update_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'medical_history': 'Updated medical history',
            'chief_complaint': 'Updated chief complaint',
            'nihss_score': 8
        }
        serializer = PatientSerializer(self.patient, data=update_data, partial=True, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        updated_patient = serializer.save()
        self.assertEqual(updated_patient.first_name, update_data['first_name'])
        self.assertEqual(updated_patient.last_name, update_data['last_name'])
        self.assertEqual(updated_patient.medical_history, update_data['medical_history'])
        self.assertEqual(updated_patient.chief_complaint, update_data['chief_complaint'])
        self.assertEqual(updated_patient.nihss_score, update_data['nihss_score'])

    def test_patient_serializer_read_only_fields(self):
        """Test that read-only fields cannot be updated"""
        update_data = {
            'created_by': 999,  # Try to change created_by
            'created_at': timezone.now()  # Try to change created_at
        }
        serializer = PatientSerializer(self.patient, data=update_data, partial=True, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        updated_patient = serializer.save()
        self.assertEqual(updated_patient.created_by, self.user)  # Should not change 