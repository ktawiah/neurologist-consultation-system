from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Patient, VitalSign, LabResult,
    ImagingStudy, NeurologistConsultation, AlertNotification
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Role', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role'),
        }),
    )

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'age', 'nihss_score', 'diagnosis', 'created_at')
    list_filter = ('sex', 'created_at')
    search_fields = ('first_name', 'last_name', 'medical_history')
    readonly_fields = ('created_at', 'updated_at')

    def age(self, obj):
        from datetime import date
        today = date.today()
        return today.year - obj.date_of_birth.year - ((today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day))

@admin.register(VitalSign)
class VitalSignAdmin(admin.ModelAdmin):
    list_display = ('patient', 'blood_pressure', 'heart_rate', 'oxygen_saturation', 'recorded_at')
    list_filter = ('recorded_at',)
    search_fields = ('patient__first_name', 'patient__last_name')

    def blood_pressure(self, obj):
        return f"{obj.blood_pressure_systolic}/{obj.blood_pressure_diastolic}"

@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ('patient', 'glucose', 'creatinine', 'recorded_at')
    list_filter = ('recorded_at',)
    search_fields = ('patient__first_name', 'patient__last_name')

@admin.register(ImagingStudy)
class ImagingStudyAdmin(admin.ModelAdmin):
    list_display = ('patient', 'study_type', 'recorded_at')
    list_filter = ('study_type', 'recorded_at')
    search_fields = ('patient__first_name', 'patient__last_name', 'findings')

@admin.register(NeurologistConsultation)
class NeurologistConsultationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'neurologist', 'diagnosis', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('patient__first_name', 'patient__last_name', 'diagnosis', 'treatment_plan')

@admin.register(AlertNotification)
class AlertNotificationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'alert_type', 'is_critical', 'created_at', 'acknowledged_at')
    list_filter = ('alert_type', 'is_critical', 'created_at', 'acknowledged_at')
    search_fields = ('patient__first_name', 'patient__last_name', 'message')
