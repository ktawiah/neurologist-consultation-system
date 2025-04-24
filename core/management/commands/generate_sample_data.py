from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Patient, VitalSign, LabResult, ImagingStudy, AlertNotification, NeurologistConsultation
from django.utils import timezone
from datetime import timedelta
import random
from faker import Faker
import os
from django.conf import settings

User = get_user_model()
fake = Faker()

class StrokeAssessment:
    @staticmethod
    def check_tpa_eligibility(vital_signs, lab_results, patient_data):
        """Check if patient meets tPA criteria"""
        exclusions = []
        
        # Check time window
        if patient_data['hours_since_onset'] > 4.5:
            exclusions.append("Outside 4.5-hour treatment window")
        
        # Check vital signs
        if vital_signs:
            if vital_signs['blood_pressure_systolic'] > 185:
                exclusions.append("Systolic BP > 185 mmHg")
            if vital_signs['blood_pressure_diastolic'] > 110:
                exclusions.append("Diastolic BP > 110 mmHg")
        
        # Check lab values
        if lab_results:
            if lab_results['glucose'] < 50 or lab_results['glucose'] > 400:
                exclusions.append("Blood glucose out of range")
            if lab_results['inr'] >= 1.7:
                exclusions.append("INR ≥ 1.7")
            if lab_results['platelet_count'] < 100000:
                exclusions.append("Platelet count < 100,000/μL")
        
        # Check NIHSS criteria
        if patient_data['nihss_score'] < 4:
            exclusions.append("NIHSS score < 4")
        
        # Check age
        if patient_data['age'] < 18:
            exclusions.append("Age < 18 years")
        
        return len(exclusions) == 0, exclusions

def generate_vital_signs(status, hours_since_onset):
    """Generate vital signs based on patient status and time since onset"""
    if status == 'critical':
        return {
            'blood_pressure_systolic': random.randint(170, 220),
            'blood_pressure_diastolic': random.randint(95, 120),
            'heart_rate': random.choice([random.randint(40, 50), random.randint(120, 150)]),
            'respiratory_rate': random.choice([random.randint(8, 10), random.randint(25, 35)]),
            'oxygen_saturation': random.randint(85, 92),
            'temperature': round(random.uniform(38.1, 39.5), 1)  # Fever
        }
    elif status == 'acute_eligible':
        return {
            'blood_pressure_systolic': random.randint(140, 185),
            'blood_pressure_diastolic': random.randint(80, 105),
            'heart_rate': random.randint(60, 100),
            'respiratory_rate': random.randint(12, 20),
            'oxygen_saturation': random.randint(95, 100),
            'temperature': round(random.uniform(36.5, 37.5), 1)
        }
    else:  # stable
        return {
            'blood_pressure_systolic': random.randint(110, 140),
            'blood_pressure_diastolic': random.randint(60, 85),
            'heart_rate': random.randint(60, 90),
            'respiratory_rate': random.randint(12, 20),
            'oxygen_saturation': random.randint(95, 100),
            'temperature': round(random.uniform(36.5, 37.5), 1)
        }

def generate_lab_results(status):
    """Generate lab results based on patient status"""
    if status == 'critical':
        return {
            'glucose': random.uniform(250, 450),
            'inr': random.uniform(2.5, 4.0),
            'platelet_count': random.randint(50000, 90000),
            'creatinine': random.uniform(2.0, 4.0)
        }
    elif status == 'acute_eligible':
        return {
            'glucose': random.uniform(70, 180),
            'inr': random.uniform(0.9, 1.6),
            'platelet_count': random.randint(150000, 400000),
            'creatinine': random.uniform(0.7, 1.4)
        }
    else:  # stable
        return {
            'glucose': random.uniform(70, 200),
            'inr': random.uniform(0.9, 3.0),
            'platelet_count': random.randint(100000, 400000),
            'creatinine': random.uniform(0.7, 1.8)
        }

class Command(BaseCommand):
    help = 'Generates production sample data with stroke protocol criteria'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write(self.style.WARNING('This command should only be run in development mode.'))
            return

        # Get credentials from environment variables with secure defaults
        neurologist_username = os.getenv('NEUROLOGIST_USERNAME', 'admin')
        neurologist_password = os.getenv('NEUROLOGIST_PASSWORD', 'admin123')
        technician_username = os.getenv('TECHNICIAN_USERNAME', 'tech')
        technician_password = os.getenv('TECHNICIAN_PASSWORD', 'tech123')

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
                'email': f'{neurologist_username}@hospital.com',
                'role': 'NEUROLOGIST',
                'is_staff': True,
                'is_superuser': True
            }
        )
        neurologist.set_password(neurologist_password)
        neurologist.save()

        technician, _ = User.objects.get_or_create(
            username=technician_username,
            defaults={
                'email': f'{technician_username}@hospital.com',
                'role': 'TECHNICIAN',
                'is_staff': True
            }
        )
        technician.set_password(technician_password)
        technician.save()

        self.stdout.write(f'Neurologist - username: {neurologist_username}')
        self.stdout.write(f'Technician - username: {technician_username}')

        self.stdout.write('Generating sample patients...')
        
        # Patient status distribution
        patient_statuses = [
            {'status': 'acute_eligible', 'weight': 0.3},  # 30% acute stroke, eligible for tPA
            {'status': 'critical', 'weight': 0.2},        # 20% critical (outside window or contraindicated)
            {'status': 'stable', 'weight': 0.5}           # 50% stable/chronic
        ]
        
        # Generate 20 patients with realistic data
        for i in range(20):
            # Determine patient status based on weights
            status = random.choices(
                [s['status'] for s in patient_statuses],
                weights=[s['weight'] for s in patient_statuses]
            )[0]

            # Generate basic patient data
            age = random.randint(40 if status != 'acute_eligible' else 18, 85)
            hours_since_onset = random.uniform(
                0.5 if status == 'acute_eligible' else 4.5,
                4.0 if status == 'acute_eligible' else 72.0
            )

            # Generate NIHSS score based on status
            if status == 'acute_eligible':
                nihss_score = random.randint(4, 22)  # Significant deficit but not devastating
            elif status == 'critical':
                nihss_score = random.randint(15, 42)  # Severe deficit
            else:
                nihss_score = random.randint(0, 8)  # Mild to moderate deficit

            patient_data = {
                'age': age,
                'hours_since_onset': hours_since_onset,
                'nihss_score': nihss_score
            }

            # Generate vital signs and lab results
            vital_signs = generate_vital_signs(status, hours_since_onset)
            lab_results = generate_lab_results(status)

            # Check tPA eligibility
            is_eligible, exclusions = StrokeAssessment.check_tpa_eligibility(
                vital_signs, lab_results, patient_data
            )

            # Create patient
            patient = Patient.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=fake.date_of_birth(minimum_age=age, maximum_age=age),
                sex=random.choice(['M', 'F']),
                nihss_score=nihss_score,
                chief_complaint=random.choice([
                    'Acute onset left-sided weakness',
                    'Sudden difficulty speaking',
                    'Right-sided facial droop',
                    'Acute onset confusion',
                    'Severe headache with neurological symptoms'
                ] if status in ['acute_eligible', 'critical'] else [
                    'Follow-up for previous stroke',
                    'Mild residual weakness',
                    'Chronic neurological symptoms',
                    'Regular stroke clinic visit'
                ]),
                medical_history=', '.join(random.sample([
                    'Hypertension',
                    'Diabetes',
                    'Atrial Fibrillation',
                    'Previous Stroke',
                    'Heart Disease',
                    'High Cholesterol',
                    'Smoking',
                    'Carotid Stenosis'
                ], random.randint(2, 5))),
                created_by=random.choice([neurologist, technician])
            )

            # Create vital signs
            for _ in range(random.randint(2, 3)):
                VitalSign.objects.create(
                    patient=patient,
                    blood_pressure_systolic=random.randint(110, 180),
                    blood_pressure_diastolic=random.randint(60, 110),
                    heart_rate=random.randint(60, 100),
                    respiratory_rate=random.randint(12, 20),
                    oxygen_saturation=random.randint(94, 100),
                    recorded_by=technician
                )

            # Create lab results
            LabResult.objects.create(
                patient=patient,
                cbc=f"WBC: {random.uniform(4.0, 11.0):.1f}, RBC: {random.uniform(4.0, 6.0):.1f}, HGB: {random.uniform(12.0, 16.0):.1f}, HCT: {random.uniform(35.0, 45.0):.1f}, PLT: {lab_results['platelet_count']}",
                bmp=f"Na: {random.randint(135,145)}, K: {random.uniform(3.5,5.0):.1f}, Cl: {random.randint(96,106)}, CO2: {random.randint(22,29)}, BUN: {random.randint(8,25)}, Cr: {lab_results['creatinine']:.1f}",
                coagulation_studies=f"PT: {random.uniform(11.0,13.0):.1f}, INR: {lab_results['inr']:.1f}, PTT: {random.randint(25,35)}",
                glucose=lab_results['glucose'],
                creatinine=lab_results['creatinine'],
                recorded_by=technician
            )

            # Create imaging study
            if status == 'acute_eligible':
                findings = [
                    'Early ischemic changes in left MCA territory',
                    'Hyperdense MCA sign without hemorrhage',
                    'Small cortical hypodensity, no hemorrhage',
                    'Subtle loss of gray-white differentiation'
                ]
            elif status == 'critical':
                findings = [
                    'Large MCA territory infarct with mass effect',
                    'Hemorrhagic transformation of ischemic stroke',
                    'Multiple bilateral acute infarcts',
                    'Extensive intracranial hemorrhage'
                ]
            else:
                findings = [
                    'Chronic small vessel ischemic changes',
                    'Old lacunar infarcts',
                    'No acute intracranial abnormality',
                    'Age-appropriate atrophy'
                ]

            ImagingStudy.objects.create(
                patient=patient,
                study_type=random.choice(['CT', 'MRI']),
                findings=random.choice(findings),
                recorded_by=technician
            )

            # Create consultation with appropriate treatment plan
            if status == 'acute_eligible' and is_eligible:
                treatment_plan = random.choice([
                    'Initiate IV tPA protocol. Close monitoring required.',
                    'Candidate for thrombolysis. Starting tPA administration.',
                    'tPA administration approved. Proceeding with protocol.'
                ])
                additional_tests = 'Repeat CT in 24 hours post-tPA. Monitor vitals q15min for 2h, then q30min for 6h.'
            elif status == 'critical' or (status == 'acute_eligible' and not is_eligible):
                treatment_plan = random.choice([
                    'Not eligible for tPA due to: ' + ', '.join(exclusions),
                    'Conservative management. Monitor for deterioration.',
                    'Consider mechanical thrombectomy if eligible.',
                    'Neurosurgery consultation for possible intervention.'
                ])
                additional_tests = 'Serial neurological checks. Repeat imaging as needed.'
            else:
                treatment_plan = random.choice([
                    'Continue current secondary prevention measures',
                    'Optimize medical management',
                    'Outpatient rehabilitation recommended',
                    'Risk factor modification'
                ])
                additional_tests = 'Follow-up in stroke clinic in 3 months'

            NeurologistConsultation.objects.create(
                patient=patient,
                neurologist=neurologist,
                diagnosis=f"{'Acute' if status in ['acute_eligible', 'critical'] else 'Chronic'} Ischemic Stroke",
                treatment_plan=treatment_plan,
                additional_tests=additional_tests
            )

            # Create appropriate alerts
            if status == 'acute_eligible' and is_eligible:
                AlertNotification.objects.create(
                    patient=patient,
                    alert_type='CRITICAL',
                    message='ACUTE STROKE ALERT - tPA Candidate',
                    is_critical=True,
                    created_by=technician
                )
            elif status == 'critical':
                AlertNotification.objects.create(
                    patient=patient,
                    alert_type='CRITICAL',
                    message=f"Critical patient status: {', '.join(exclusions)}",
                    is_critical=True,
                    created_by=technician
                )
            elif status == 'acute_eligible' and not is_eligible:
                AlertNotification.objects.create(
                    patient=patient,
                    alert_type='WARNING',
                    message=f"Acute stroke - not tPA eligible: {', '.join(exclusions)}",
                    is_critical=False,
                    created_by=technician
                )

        self.stdout.write(self.style.SUCCESS('Successfully generated production sample data'))
        self.stdout.write('\nTest users created:')
        self.stdout.write(f'Neurologist - username: {neurologist_username}')
        self.stdout.write(f'Technician - username: {technician_username}')
        self.stdout.write('\nPlease change these passwords immediately after first login!') 