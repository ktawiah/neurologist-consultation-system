from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Patient, VitalSign, LabResult, ImagingStudy, NeurologistConsultation
from datetime import datetime, date

User = get_user_model()

class Command(BaseCommand):
    help = 'Loads sample patient data into the database'

    def handle(self, *args, **kwargs):
        # Create users if they don't exist
        technician, _ = User.objects.get_or_create(
            username='technician',
            defaults={
                'email': 'technician@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': User.Role.MOBILE_TECHNICIAN
            }
        )
        technician.set_password('password123')
        technician.save()

        neurologist, _ = User.objects.get_or_create(
            username='neurologist',
            defaults={
                'email': 'neurologist@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'role': User.Role.NEUROLOGIST
            }
        )
        neurologist.set_password('password123')
        neurologist.save()

        # Sample patients data
        patients_data = [
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'date_of_birth': date(1958, 5, 15),
                'sex': 'M',
                'medical_history': 'Hypertension, hyperlipidemia, diabetes',
                'chief_complaint': 'Sudden onset of weakness in the left arm and leg',
                'nihss_score': 12,
                'vitals': {
                    'blood_pressure_systolic': 180,
                    'blood_pressure_diastolic': 100,
                    'heart_rate': 100,
                    'respiratory_rate': 20,
                    'oxygen_saturation': 95
                },
                'labs': {
                    'cbc': 'Normal',
                    'bmp': 'Elevated glucose (200 mg/dL)',
                    'coagulation_studies': 'Normal',
                    'glucose': 200,
                    'creatinine': None
                },
                'imaging': {
                    'study_type': 'CT',
                    'findings': 'Large infarct in the right middle cerebral artery territory'
                },
                'consultation': {
                    'diagnosis': 'Acute ischemic stroke',
                    'treatment_plan': 'tPA administration, blood pressure management, and admission to the ICU',
                    'additional_tests': 'None'
                }
            },
            {
                'first_name': 'Jane',
                'last_name': 'Smith',
                'date_of_birth': date(1973, 8, 22),
                'sex': 'F',
                'medical_history': 'None',
                'chief_complaint': 'Sudden onset of difficulty speaking and understanding speech',
                'nihss_score': 8,
                'vitals': {
                    'blood_pressure_systolic': 120,
                    'blood_pressure_diastolic': 80,
                    'heart_rate': 80,
                    'respiratory_rate': 16,
                    'oxygen_saturation': 98
                },
                'labs': {
                    'cbc': 'Normal',
                    'bmp': 'Normal',
                    'coagulation_studies': 'Normal',
                    'glucose': None,
                    'creatinine': None
                },
                'imaging': {
                    'study_type': 'CT',
                    'findings': 'Small infarct in the left posterior cerebral artery territory'
                },
                'consultation': {
                    'diagnosis': 'Acute ischemic stroke',
                    'treatment_plan': 'tPA administration, speech therapy, and admission to the hospital for close monitoring',
                    'additional_tests': 'None'
                }
            }
        ]

        for patient_data in patients_data:
            # Create patient
            patient = Patient.objects.create(
                first_name=patient_data['first_name'],
                last_name=patient_data['last_name'],
                date_of_birth=patient_data['date_of_birth'],
                sex=patient_data['sex'],
                medical_history=patient_data['medical_history'],
                chief_complaint=patient_data['chief_complaint'],
                nihss_score=patient_data['nihss_score'],
                created_by=technician
            )

            # Create vital signs
            VitalSign.objects.create(
                patient=patient,
                recorded_by=technician,
                **patient_data['vitals']
            )

            # Create lab results
            LabResult.objects.create(
                patient=patient,
                recorded_by=technician,
                **patient_data['labs']
            )

            # Create imaging study
            ImagingStudy.objects.create(
                patient=patient,
                recorded_by=technician,
                **patient_data['imaging']
            )

            # Create consultation
            NeurologistConsultation.objects.create(
                patient=patient,
                neurologist=neurologist,
                **patient_data['consultation']
            )

        self.stdout.write(self.style.SUCCESS('Successfully loaded sample data')) 