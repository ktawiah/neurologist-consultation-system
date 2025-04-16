from django.urls import path
from .views import (
    dashboard, PatientListView, PatientDetailView,
    PatientCreateView, PatientUpdateView, alert_acknowledge,
    AlertListView, ConsultationCreateView, VitalSignCreateView,
    LabResultCreateView, login_view, SignUpView
)

urlpatterns = [
    # Authentication URLs
    path('login/', login_view, name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    
    # Frontend URLs
    path('', dashboard, name='dashboard'),
    path('patients/', PatientListView.as_view(), name='patient_list'),
    path('patients/<int:pk>/', PatientDetailView.as_view(), name='patient_detail'),
    path('patients/new/', PatientCreateView.as_view(), name='patient_create'),
    path('patients/<int:pk>/edit/', PatientUpdateView.as_view(), name='patient_edit'),
    path('alerts/', AlertListView.as_view(), name='alerts'),
    path('alerts/<int:pk>/acknowledge/', alert_acknowledge, name='alert_acknowledge'),
    path('consultations/new/<int:patient_id>/', ConsultationCreateView.as_view(), name='consultation_create'),
    path('vital-signs/new/<int:patient_id>/', VitalSignCreateView.as_view(), name='vital_sign_create'),
    path('lab-results/new/<int:patient_id>/', LabResultCreateView.as_view(), name='lab_result_create'),
] 