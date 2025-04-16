from django.db import models
from .user import User
from .patient import Patient
from .notification import AlertNotification

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
            # Check blood pressure - Critical, Warning, and Info levels
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
            elif self.blood_pressure_systolic >= 140 or self.blood_pressure_diastolic >= 90:
                AlertNotification.objects.create(
                    patient=self.patient,
                    alert_type=AlertNotification.AlertType.INFO,
                    message=f'Elevated BP: {self.blood_pressure_systolic}/{self.blood_pressure_diastolic} mmHg',
                    created_by=self.recorded_by
                )

            # Check heart rate - Critical and Warning levels
            if self.heart_rate >= 120 or self.heart_rate <= 50:
                AlertNotification.objects.create(
                    patient=self.patient,
                    alert_type=AlertNotification.AlertType.CRITICAL,
                    message=f'Critical heart rate: {self.heart_rate} bpm',
                    is_critical=True,
                    created_by=self.recorded_by
                )
            elif self.heart_rate >= 100 or self.heart_rate <= 60:
                AlertNotification.objects.create(
                    patient=self.patient,
                    alert_type=AlertNotification.AlertType.WARNING,
                    message=f'Abnormal heart rate: {self.heart_rate} bpm',
                    created_by=self.recorded_by
                )

            # Check oxygen saturation - Critical, Warning, and Info levels
            if self.oxygen_saturation < 90:
                AlertNotification.objects.create(
                    patient=self.patient,
                    alert_type=AlertNotification.AlertType.CRITICAL,
                    message=f'Severe hypoxemia: {self.oxygen_saturation}%',
                    is_critical=True,
                    created_by=self.recorded_by
                )
            elif self.oxygen_saturation < 94:
                AlertNotification.objects.create(
                    patient=self.patient,
                    alert_type=AlertNotification.AlertType.WARNING,
                    message=f'Low oxygen saturation: {self.oxygen_saturation}%',
                    created_by=self.recorded_by
                )
            elif self.oxygen_saturation < 96:
                AlertNotification.objects.create(
                    patient=self.patient,
                    alert_type=AlertNotification.AlertType.INFO,
                    message=f'Borderline oxygen saturation: {self.oxygen_saturation}%',
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
            # Check glucose levels - Critical, Warning, and Info levels
            if self.glucose:
                if self.glucose > 400 or self.glucose < 50:
                    AlertNotification.objects.create(
                        patient=self.patient,
                        alert_type=AlertNotification.AlertType.CRITICAL,
                        message=f'Critical glucose level: {self.glucose} mg/dL',
                        is_critical=True,
                        created_by=self.recorded_by
                    )
                elif self.glucose > 200 or self.glucose < 70:
                    AlertNotification.objects.create(
                        patient=self.patient,
                        alert_type=AlertNotification.AlertType.WARNING,
                        message=f'Abnormal glucose level: {self.glucose} mg/dL',
                        created_by=self.recorded_by
                    )
                elif self.glucose > 140:
                    AlertNotification.objects.create(
                        patient=self.patient,
                        alert_type=AlertNotification.AlertType.INFO,
                        message=f'Elevated glucose level: {self.glucose} mg/dL',
                        created_by=self.recorded_by
                    )

            # Check creatinine levels
            if self.creatinine:
                if self.creatinine > 2.0:
                    AlertNotification.objects.create(
                        patient=self.patient,
                        alert_type=AlertNotification.AlertType.CRITICAL,
                        message=f'Critical creatinine level: {self.creatinine} mg/dL',
                        is_critical=True,
                        created_by=self.recorded_by
                    )
                elif self.creatinine > 1.5:
                    AlertNotification.objects.create(
                        patient=self.patient,
                        alert_type=AlertNotification.AlertType.WARNING,
                        message=f'High creatinine level: {self.creatinine} mg/dL',
                        created_by=self.recorded_by
                    )
                elif self.creatinine > 1.2:
                    AlertNotification.objects.create(
                        patient=self.patient,
                        alert_type=AlertNotification.AlertType.INFO,
                        message=f'Elevated creatinine level: {self.creatinine} mg/dL',
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
