from django.test import TestCase
from django.core.exceptions import ValidationError
from core.forms.patient import PatientForm
from core.models.user import User
from core.models.patient import Patient

class PatientFormsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.patient_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1990-01-01',
            'sex': Patient.Sex.MALE,
            'medical_history': 'No significant medical history',
            'chief_complaint': 'Headache and dizziness',
            'nihss_score': 5
        }

    def test_patient_form_valid(self):
        """Test that the patient form works with valid data"""
        form = PatientForm(data=self.patient_data)
        self.assertTrue(form.is_valid())
        patient = form.save(commit=False)
        patient.created_by = self.user
        patient.save()
        self.assertEqual(patient.first_name, self.patient_data['first_name'])
        self.assertEqual(patient.last_name, self.patient_data['last_name'])
        self.assertEqual(str(patient.date_of_birth), self.patient_data['date_of_birth'])
        self.assertEqual(patient.sex, self.patient_data['sex'])
        self.assertEqual(patient.medical_history, self.patient_data['medical_history'])
        self.assertEqual(patient.chief_complaint, self.patient_data['chief_complaint'])
        self.assertEqual(patient.nihss_score, self.patient_data['nihss_score'])

    def test_patient_form_required_fields(self):
        """Test that required fields are properly validated"""
        form = PatientForm(data={})
        self.assertFalse(form.is_valid())
        required_fields = ['first_name', 'last_name', 'date_of_birth', 'sex', 
                         'chief_complaint', 'nihss_score']
        for field in required_fields:
            self.assertIn(field, form.errors)

    def test_patient_form_nihss_score_validation(self):
        """Test that NIHSS score is properly validated"""
        data = self.patient_data.copy()
        data['nihss_score'] = -1  # Invalid NIHSS score
        form = PatientForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('nihss_score', form.errors)

        data['nihss_score'] = 42  # Valid NIHSS score
        form = PatientForm(data=data)
        self.assertTrue(form.is_valid())

    def test_patient_form_date_validation(self):
        """Test that date of birth is properly validated"""
        data = self.patient_data.copy()
        data['date_of_birth'] = 'invalid-date'  # Invalid date format
        form = PatientForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_of_birth', form.errors)

        data['date_of_birth'] = '2100-01-01'  # Future date
        form = PatientForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_of_birth', form.errors)

    def test_patient_form_update(self):
        """Test updating an existing patient"""
        patient = Patient.objects.create(
            first_name='Original',
            last_name='Name',
            date_of_birth='1990-01-01',
            sex=Patient.Sex.MALE,
            medical_history='Original history',
            chief_complaint='Original complaint',
            nihss_score=5,
            created_by=self.user
        )
        form_data = self.patient_data.copy()
        form = PatientForm(data=form_data, instance=patient)
        self.assertTrue(form.is_valid())
        updated_patient = form.save()
        self.assertEqual(updated_patient.first_name, form_data['first_name'])
        self.assertEqual(updated_patient.last_name, form_data['last_name'])
        self.assertEqual(updated_patient.medical_history, form_data['medical_history'])
        self.assertEqual(updated_patient.chief_complaint, form_data['chief_complaint'])
        self.assertEqual(updated_patient.nihss_score, form_data['nihss_score']) 