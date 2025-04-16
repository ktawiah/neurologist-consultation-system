from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Patient, VitalSign, LabResult, ImagingStudy, AlertNotification, NeurologistConsultation
from django.utils import timezone
from datetime import timedelta
import random
from faker import Faker
import os

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Generates sample data for testing'

    def handle(self, *args, **options):
        # Get credentials from environment variables
        neurologist_username = os.getenv('NEUROLOGIST_USERNAME', 'neurologist')
        neurologist_password = os.getenv('NEUROLOGIST_PASSWORD', 'neurologist123')
        technician_username = os.getenv('TECHNICIAN_USERNAME', 'technician')
        technician_password = os.getenv('TECHNICIAN_PASSWORD', 'technician123')

        self.stdout.write('Clearing existing data...')
        # Clear existing data
        AlertNotification.objects.all().delete()
        NeurologistConsultation.objects.all().delete()
        ImagingStudy.objects.all().delete()
        LabResult.objects.all().delete()
        VitalSign.objects.all().delete()
        Patient.objects.all().delete()

        # Create or get users
        neurologist, _ = User.objects.get_or_create(
            username=neurologist_username,
            defaults={
                'email': f'{neurologist_username}@example.com',
                'role': 'NEUROLOGIST'
            }
        )
        neurologist.set_password(neurologist_password)
        neurologist.save()

        technician, _ = User.objects.get_or_create(
            username=technician_username,
            defaults={
                'email': f'{technician_username}@example.com',
                'role': 'TECHNICIAN'
            }
        )
        technician.set_password(technician_password)
        technician.save()

        self.stdout.write(f'Neurologist - username: {neurologist_username}')
        self.stdout.write(f'Technician - username: {technician_username}')

        self.stdout.write('Generating sample patients...')
        
        # Generate 50 patients with varied data
        for i in range(50):
            # Create patient
            patient = Patient.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=fake.date_of_birth(minimum_age=25, maximum_age=90),
                sex=random.choice(['M', 'F']),
                nihss_score=random.randint(0, 42),
                chief_complaint=random.choice([
                    'Sudden weakness in left arm',
                    'Difficulty speaking',
                    'Severe headache',
                    'Vision problems',
                    'Balance issues',
                    'Numbness in right side',
                    'Confusion and dizziness'
                ]),
                medical_history=', '.join(random.sample([
                    'Hypertension',
                    'Diabetes',
                    'Atrial Fibrillation',
                    'Previous Stroke',
                    'Heart Disease',
                    'High Cholesterol',
                    'Obesity'
                ], random.randint(0, 4))),
                created_by=random.choice([neurologist, technician])
            )

            # Generate vital signs (1-5 records per patient)
            for _ in range(random.randint(1, 5)):
                VitalSign.objects.create(
                    patient=patient,
                    blood_pressure_systolic=random.randint(100, 180),
                    blood_pressure_diastolic=random.randint(60, 100),
                    heart_rate=random.randint(60, 100),
                    respiratory_rate=random.randint(12, 20),
                    oxygen_saturation=random.randint(88, 100),
                    recorded_by=technician,
                    recorded_at=timezone.now() - timedelta(hours=random.randint(0, 72))
                )

            # Generate lab results (0-3 records per patient)
            for _ in range(random.randint(0, 3)):
                LabResult.objects.create(
                    patient=patient,
                    glucose=random.uniform(70, 200),
                    creatinine=random.uniform(0.5, 2.0),
                    recorded_by=technician,
                    recorded_at=timezone.now() - timedelta(hours=random.randint(0, 72))
                )

            # Generate imaging studies (0-2 records per patient)
            study_types = ['CT', 'MRI', 'CTA', 'MRA']
            for _ in range(random.randint(0, 2)):
                study_type = random.choice(study_types)
                ImagingStudy.objects.create(
                    patient=patient,
                    study_type=study_type,
                    findings=f"{study_type} shows {'evidence of acute stroke' if random.random() > 0.5 else 'no acute findings'}",
                    recorded_by=technician,
                    recorded_at=timezone.now() - timedelta(hours=random.randint(0, 72))
                )

            # Generate consultations (0-2 records per patient)
            for _ in range(random.randint(0, 2)):
                diagnosis = random.choice([
                    'Acute Ischemic Stroke',
                    'Hemorrhagic Stroke',
                    'Transient Ischemic Attack',
                    'Stroke Mimics',
                    'Cerebral Venous Thrombosis'
                ])
                treatment_plan = random.choice([
                    'Initiate IV thrombolysis with tPA. Monitor closely for hemorrhagic transformation.',
                    'Conservative management with blood pressure control and neurological monitoring.',
                    'Mechanical thrombectomy evaluation. Transfer to comprehensive stroke center.',
                    'Anticoagulation therapy with continuous monitoring.',
                    'Supportive care and rehabilitation planning.'
                ])
                additional_tests = random.choice([
                    'Schedule follow-up MRI in 24 hours',
                    'Carotid ultrasound to evaluate stenosis',
                    'Holter monitor for AF detection',
                    'Echocardiogram to rule out cardiac source',
                    ''
                ])
                
                NeurologistConsultation.objects.create(
                    patient=patient,
                    neurologist=neurologist,
                    diagnosis=diagnosis,
                    treatment_plan=treatment_plan,
                    additional_tests=additional_tests,
                    created_at=timezone.now() - timedelta(hours=random.randint(0, 72))
                )

            # Generate alerts (0-3 records per patient)
            for _ in range(random.randint(0, 3)):
                is_critical = random.random() > 0.7
                AlertNotification.objects.create(
                    patient=patient,
                    alert_type=random.choice(['VS', 'LB', 'IM', 'OT']),
                    message=random.choice([
                        'Critical NIHSS score increase',
                        'Abnormal blood pressure reading',
                        'Urgent lab result notification',
                        'Imaging study results available',
                        'Patient condition deteriorating'
                    ]),
                    is_critical=is_critical,
                    created_by=technician,
                    created_at=timezone.now() - timedelta(hours=random.randint(0, 72)),
                    acknowledged_at=timezone.now() - timedelta(hours=random.randint(0, 24)) if random.random() > 0.5 else None,
                    acknowledged_by=neurologist if random.random() > 0.5 else None
                )

        self.stdout.write(self.style.SUCCESS('Successfully generated sample data'))
        self.stdout.write('\nTest users created:')
        self.stdout.write(f'Neurologist - username: {neurologist_username}')
        self.stdout.write(f'Technician - username: {technician_username}') 