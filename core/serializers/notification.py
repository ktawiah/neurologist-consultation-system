from rest_framework import serializers
from ..models import AlertNotification

class AlertNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertNotification
        fields = (
            'id', 'patient', 'alert_type', 'message', 'is_critical',
            'created_at', 'created_by', 'acknowledged_by', 'acknowledged_at'
        )
