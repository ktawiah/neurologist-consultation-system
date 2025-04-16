from rest_framework import serializers
from datetime import date
from core.models.patient import Patient

class PatientSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()
    has_critical_alerts = serializers.BooleanField(read_only=True)
    has_pending_consultation = serializers.BooleanField(read_only=True)
    date_of_birth = serializers.DateField(format='%Y-%m-%d')

    class Meta:
        model = Patient
        fields = ('id', 'first_name', 'last_name', 'date_of_birth', 'sex',
                 'medical_history', 'chief_complaint', 'nihss_score',
                 'created_by', 'created_at', 'age', 'has_critical_alerts',
                 'has_pending_consultation')
        read_only_fields = ('created_by', 'created_at', 'age', 'has_critical_alerts',
                          'has_pending_consultation')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'date_of_birth': {'required': True},
            'sex': {'required': True},
            'chief_complaint': {'required': True},
            'nihss_score': {'required': True},
        }

    def get_age(self, obj):
        today = date.today()
        dob = obj.date_of_birth
        if isinstance(dob, str):
            from datetime import datetime
            dob = datetime.strptime(dob, '%Y-%m-%d').date()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def validate_nihss_score(self, value):
        if value < 0 or value > 42:
            raise serializers.ValidationError("NIHSS score must be between 0 and 42.")
        return value

    def validate_date_of_birth(self, value):
        if value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    def create(self, validated_data):
        if 'request' in self.context:
            validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
