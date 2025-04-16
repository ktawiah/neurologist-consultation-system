from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    class Role(models.TextChoices):
        MOBILE_TECHNICIAN = 'MT', 'Mobile Technician'
        NEUROLOGIST = 'NR', 'Neurologist'
    
    role = models.CharField(
        max_length=2,
        choices=Role.choices,
        default=Role.MOBILE_TECHNICIAN
    )

class Patient(models.Model):
    class Sex(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=1, choices=Sex.choices)
    medical_history = models.TextField(blank=True)
    chief_complaint = models.TextField()
    nihss_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_patients')
    
    # Outcome fields
    diagnosis = models.CharField(max_length=200, blank=True)
    treatment = models.TextField(blank=True)
    outcome = models.TextField(blank=True)
    disposition = models.CharField(max_length=200, blank=True)
    follow_up_plan = models.TextField(blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if not is_new and self.nihss_score >= 10:  # Check NIHSS score on updates
            AlertNotification.objects.create(
                patient=self,
                alert_type=AlertNotification.AlertType.CRITICAL,
                message=f'High NIHSS Score: {self.nihss_score}',
                is_critical=True,
                created_by=self.created_by
            )

class VitalSign(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vital_signs')
    blood_pressure_systolic = models.IntegerField()
    blood_pressure_diastolic = models.IntegerField()
    heart_rate = models.IntegerField()
    respiratory_rate = models.IntegerField()
    oxygen_saturation = models.IntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-recorded_at']

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:  # Only check for alerts on new vital signs
            # Check blood pressure
            if self.blood_pressure_systolic >= 180 or self.blood_pressure_diastolic >= 120:
                AlertNotification.objects.create(
                    patient=self.patient,
                    alert_type=AlertNotification.AlertType.CRITICAL,
                    message=f'Critical BP: {self.blood_pressure_systolic}/{self.blood_pressure_diastolic} mmHg',
                    is_critical=True,
                    created_by=self.recorded_by
                )
            elif self.blood_pressure_systolic >= 160 or self.blood_pressure_diastolic >= 100:
                AlertNotification.objects.create(
                    patient=self.patient,
                    alert_type=AlertNotification.AlertType.WARNING,
                    message=f'High BP: {self.blood_pressure_systolic}/{self.blood_pressure_diastolic} mmHg',
                    created_by=self.recorded_by
                )

            # Check heart rate
            if self.heart_rate >= 120 or self.heart_rate <= 50:
                AlertNotification.objects.create(
                    patient=self.patient,
                    alert_type=AlertNotification.AlertType.CRITICAL,
                    message=f'Abnormal heart rate: {self.heart_rate} bpm',
                    is_critical=True,
                    created_by=self.recorded_by
                )

            # Check oxygen saturation
            if self.oxygen_saturation < 92:
                AlertNotification.objects.create(
                    patient=self.patient,
                    alert_type=AlertNotification.AlertType.CRITICAL,
                    message=f'Low oxygen saturation: {self.oxygen_saturation}%',
                    is_critical=True,
                    created_by=self.recorded_by
                )

class LabResult(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_results')
    cbc = models.TextField(blank=True)
    bmp = models.TextField(blank=True)
    coagulation_studies = models.TextField(blank=True)
    glucose = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    creatinine = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-recorded_at']

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:  # Only check for alerts on new lab results
            # Check glucose levels
            if self.glucose and self.glucose > 180:
                AlertNotification.objects.create(
                    patient=self.patient,
                    alert_type=AlertNotification.AlertType.WARNING,
                    message=f'High glucose level: {self.glucose} mg/dL',
                    created_by=self.recorded_by
                )
            elif self.glucose and self.glucose < 70:
                AlertNotification.objects.create(
                    patient=self.patient,
                    alert_type=AlertNotification.AlertType.CRITICAL,
                    message=f'Low glucose level: {self.glucose} mg/dL',
                    is_critical=True,
                    created_by=self.recorded_by
                )

class ImagingStudy(models.Model):
    class StudyType(models.TextChoices):
        CT = 'CT', 'CT Scan'
        MRI = 'MRI', 'MRI'

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='imaging_studies')
    study_type = models.CharField(max_length=3, choices=StudyType.choices)
    findings = models.TextField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-recorded_at']

class NeurologistConsultation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consultations')
    neurologist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='consultations')
    diagnosis = models.CharField(max_length=200)
    treatment_plan = models.TextField()
    additional_tests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:  # Create alert for new consultations
            AlertNotification.objects.create(
                patient=self.patient,
                alert_type=AlertNotification.AlertType.INFO,
                message=f'New neurologist consultation by {self.neurologist.get_full_name()}',
                created_by=self.neurologist
            )

class AlertNotification(models.Model):
    class AlertType(models.TextChoices):
        CRITICAL = 'CR', 'Critical'
        WARNING = 'WR', 'Warning'
        INFO = 'IN', 'Information'

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=2, choices=AlertType.choices)
    message = models.TextField()
    is_critical = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_alerts')
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='acknowledged_alerts')
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
