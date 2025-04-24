from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView
from .views import (
    dashboard, PatientListView, PatientDetailView,
    PatientCreateView, PatientUpdateView, alert_acknowledge,
    AlertListView, ConsultationCreateView, VitalSignCreateView,
    LabResultCreateView, login_view, SignUpView, ImagingStudyCreateView,
    VitalSignUpdateView, VitalSignDeleteView,
    LabResultUpdateView, LabResultDeleteView,
    ImagingStudyUpdateView, ImagingStudyDeleteView,
    ConsultationUpdateView, ConsultationDeleteView
)

urlpatterns = [
    # Root URL - redirects to dashboard if authenticated, otherwise shows login
    path('', login_required(RedirectView.as_view(pattern_name='dashboard'), login_url='login/'), name='root'),
    
    # Authentication URLs
    path('login/', login_view, name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    
    # Frontend URLs
    path('dashboard/', dashboard, name='dashboard'),
    path('patients/', PatientListView.as_view(), name='patient_list'),
    path('patients/<int:pk>/', PatientDetailView.as_view(), name='patient_detail'),
    path('patients/new/', PatientCreateView.as_view(), name='patient_create'),
    path('patients/<int:pk>/edit/', PatientUpdateView.as_view(), name='patient_edit'),
    path('alerts/', AlertListView.as_view(), name='alerts'),
    path('alerts/<int:pk>/acknowledge/', alert_acknowledge, name='alert_acknowledge'),
    
    # Vital Signs URLs
    path('vital-signs/new/<int:patient_id>/', VitalSignCreateView.as_view(), name='vital_sign_create'),
    path('vital-signs/<int:pk>/update/', VitalSignUpdateView.as_view(), name='vital_sign_update'),
    path('vital-signs/<int:pk>/delete/', VitalSignDeleteView.as_view(), name='vital_sign_delete'),
    
    # Lab Results URLs
    path('lab-results/new/<int:patient_id>/', LabResultCreateView.as_view(), name='lab_result_create'),
    path('lab-results/<int:pk>/update/', LabResultUpdateView.as_view(), name='lab_result_update'),
    path('lab-results/<int:pk>/delete/', LabResultDeleteView.as_view(), name='lab_result_delete'),
    
    # Imaging Studies URLs
    path('patient/<int:patient_id>/imaging-study/create/', ImagingStudyCreateView.as_view(), name='imaging_study_create'),
    path('imaging-study/<int:pk>/update/', ImagingStudyUpdateView.as_view(), name='imaging_study_update'),
    path('imaging-study/<int:pk>/delete/', ImagingStudyDeleteView.as_view(), name='imaging_study_delete'),
    
    # Consultation URLs
    path('consultations/new/<int:patient_id>/', ConsultationCreateView.as_view(), name='consultation_create'),
    path('consultations/<int:pk>/update/', ConsultationUpdateView.as_view(), name='consultation_update'),
    path('consultations/<int:pk>/delete/', ConsultationDeleteView.as_view(), name='consultation_delete'),
] 