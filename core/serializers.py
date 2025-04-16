from rest_framework import serializers
from .models import (
    User, Patient, VitalSign, LabResult, 
    ImagingStudy, NeurologistConsultation, AlertNotification
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = ['id']

class VitalSignSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalSign
        fields = [
            'id', 'patient', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'heart_rate', 'respiratory_rate', 'oxygen_saturation',
            'recorded_at', 'recorded_by'
        ]
        read_only_fields = ['id', 'recorded_at']

class LabResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabResult
        fields = [
            'id', 'patient', 'cbc', 'bmp', 'coagulation_studies',
            'glucose', 'creatinine', 'recorded_at', 'recorded_by'
        ]
        read_only_fields = ['id', 'recorded_at']

class ImagingStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagingStudy
        fields = [
            'id', 'patient', 'study_type', 'findings',
            'recorded_at', 'recorded_by'
        ]
        read_only_fields = ['id', 'recorded_at']

class NeurologistConsultationSerializer(serializers.ModelSerializer):
    neurologist_name = serializers.SerializerMethodField()

    class Meta:
        model = NeurologistConsultation
        fields = [
            'id', 'patient', 'neurologist', 'neurologist_name', 'notes',
            'recommendations', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_neurologist_name(self, obj):
        return obj.neurologist.get_full_name() if obj.neurologist else None

class AlertNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertNotification
        fields = [
            'id', 'patient', 'alert_type', 'message', 'is_critical',
            'created_at', 'created_by', 'acknowledged_by', 'acknowledged_at'
        ]
        read_only_fields = ['id', 'created_at']

class PatientSerializer(serializers.ModelSerializer):
    vital_signs = VitalSignSerializer(many=True, read_only=True, source='vital_signs.all')
    lab_results = LabResultSerializer(many=True, read_only=True, source='labresult_set.all')
    consultations = NeurologistConsultationSerializer(many=True, read_only=True, source='neurologistconsultation_set.all')
    age = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            'id', 'first_name', 'last_name', 'date_of_birth', 'sex', 'age',
            'medical_history', 'chief_complaint', 'nihss_score',
            'diagnosis', 'treatment', 'outcome', 'disposition', 'follow_up_plan',
            'created_at', 'updated_at', 'created_by',
            'vital_signs', 'lab_results', 'consultations'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_age(self, obj):
        from datetime import date
        today = date.today()
        born = obj.date_of_birth
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return age 