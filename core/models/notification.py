from django.db import models
from .user import User
from .patient import Patient

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
