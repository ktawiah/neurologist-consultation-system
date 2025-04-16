from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import VitalSign, AlertNotification, User

@receiver(post_save, sender=VitalSign)
def create_critical_alert(sender, instance, created, **kwargs):
    if created:
        # Check for critical conditions
        is_critical = False
        message = []

        if instance.blood_pressure_systolic > 160 or instance.blood_pressure_diastolic > 100:
            is_critical = True
            message.append(f"Critical blood pressure: {instance.blood_pressure_systolic}/{instance.blood_pressure_diastolic}")

        if instance.oxygen_saturation < 93:
            is_critical = True
            message.append(f"Low oxygen saturation: {instance.oxygen_saturation}%")

        if is_critical:
            # Get all neurologists
            neurologists = User.objects.filter(role=User.Role.NEUROLOGIST)
            
            # Create alerts for each neurologist
            for neurologist in neurologists:
                AlertNotification.objects.create(
                    patient=instance.patient,
                    alert_type='CR',
                    message=' | '.join(message),
                    is_critical=True,
                    created_by=instance.recorded_by
                ) 