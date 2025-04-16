from rest_framework import serializers
from ..models import VitalSign, LabResult, ImagingStudy, NeurologistConsultation

class VitalSignSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalSign
        fields = ('id', 'patient', 'blood_pressure_systolic', 'blood_pressure_diastolic',
                 'heart_rate', 'respiratory_rate', 'oxygen_saturation', 'recorded_by',
                 'recorded_at')
        read_only_fields = ('recorded_by', 'recorded_at')
        extra_kwargs = {
            'patient': {'required': True},
            'blood_pressure_systolic': {'required': True},
            'blood_pressure_diastolic': {'required': True},
            'heart_rate': {'required': True},
            'respiratory_rate': {'required': True},
            'oxygen_saturation': {'required': True},
        }

    def validate_blood_pressure_systolic(self, value):
        if value < 0:
            raise serializers.ValidationError("Systolic blood pressure cannot be negative.")
        return value

    def validate_blood_pressure_diastolic(self, value):
        if value < 0:
            raise serializers.ValidationError("Diastolic blood pressure cannot be negative.")
        return value

    def validate_heart_rate(self, value):
        if value < 0:
            raise serializers.ValidationError("Heart rate cannot be negative.")
        return value

    def validate_respiratory_rate(self, value):
        if value < 0:
            raise serializers.ValidationError("Respiratory rate cannot be negative.")
        return value

    def validate_oxygen_saturation(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Oxygen saturation must be between 0 and 100.")
        return value

    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)

class LabResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabResult
        fields = ('id', 'patient', 'cbc', 'bmp', 'coagulation_studies',
                 'glucose', 'creatinine', 'recorded_by', 'recorded_at')
        read_only_fields = ('recorded_by', 'recorded_at')
        extra_kwargs = {
            'patient': {'required': True},
        }

    def validate_glucose(self, value):
        if value < 0:
            raise serializers.ValidationError("Glucose level cannot be negative.")
        return value

    def validate_creatinine(self, value):
        if value < 0:
            raise serializers.ValidationError("Creatinine level cannot be negative.")
        return value

    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)

class ImagingStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagingStudy
        fields = ('id', 'patient', 'study_type', 'findings', 'recorded_by', 'recorded_at')
        read_only_fields = ('recorded_by', 'recorded_at')
        extra_kwargs = {
            'patient': {'required': True},
            'study_type': {'required': True},
            'findings': {'required': True},
        }

    def validate_study_type(self, value):
        if value not in [choice[0] for choice in ImagingStudy.StudyType.choices]:
            raise serializers.ValidationError("Invalid study type.")
        return value

    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)

class NeurologistConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NeurologistConsultation
        fields = (
            'id', 'patient', 'neurologist', 'diagnosis',
            'treatment_plan', 'additional_tests',
            'created_at', 'updated_at'
        )
