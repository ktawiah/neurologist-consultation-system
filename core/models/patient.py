from django.db import models
from django.utils import timezone
from datetime import date, timedelta
from .user import User

# Model for Patient

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

    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    @property
    def has_critical_alerts(self):
        return self.alerts.filter(
            is_critical=True,
            acknowledged_at__isnull=True,
            created_at__gte=timezone.now() - timedelta(days=1)
        ).exists()

    @property
    def has_pending_consultation(self):
        last_consultation = self.consultations.order_by('-created_at').first()
        if not last_consultation:
            return True
        return (timezone.now() - last_consultation.created_at) > timedelta(hours=24)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if not is_new and self.nihss_score >= 10:  # Check NIHSS score on updates
            from .notification import AlertNotification
            AlertNotification.objects.create(
                patient=self,
                alert_type=AlertNotification.AlertType.CRITICAL,
                message=f'High NIHSS Score: {self.nihss_score}',
                is_critical=True,
                created_by=self.created_by
            )
