from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView, TemplateView
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
    # Root URL - shows landing page
    path('', TemplateView.as_view(template_name='core/landing.html'), name='landing'),
    
    # Authentication URLs
    path('login/', login_view, name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    
    # Frontend URLs
    path('dashboard/', login_required(dashboard), name='dashboard'),
    path('patients/', login_required(PatientListView.as_view()), name='patient_list'),
    path('patients/<int:pk>/', login_required(PatientDetailView.as_view()), name='patient_detail'),
    path('patients/new/', login_required(PatientCreateView.as_view()), name='patient_create'),
    path('patients/<int:pk>/edit/', login_required(PatientUpdateView.as_view()), name='patient_edit'),
    path('alerts/', login_required(AlertListView.as_view()), name='alerts'),
    path('alerts/<int:pk>/acknowledge/', login_required(alert_acknowledge), name='alert_acknowledge'),
    
    # Vital Signs URLs
    path('vital-signs/new/<int:patient_id>/', login_required(VitalSignCreateView.as_view()), name='vital_sign_create'),
    path('vital-signs/<int:pk>/update/', login_required(VitalSignUpdateView.as_view()), name='vital_sign_update'),
    path('vital-signs/<int:pk>/delete/', login_required(VitalSignDeleteView.as_view()), name='vital_sign_delete'),
    
    # Lab Results URLs
    path('lab-results/new/<int:patient_id>/', login_required(LabResultCreateView.as_view()), name='lab_result_create'),
    path('lab-results/<int:pk>/update/', login_required(LabResultUpdateView.as_view()), name='lab_result_update'),
    path('lab-results/<int:pk>/delete/', login_required(LabResultDeleteView.as_view()), name='lab_result_delete'),
    
    # Imaging Studies URLs
    path('patient/<int:patient_id>/imaging-study/create/', login_required(ImagingStudyCreateView.as_view()), name='imaging_study_create'),
    path('imaging-study/<int:pk>/update/', login_required(ImagingStudyUpdateView.as_view()), name='imaging_study_update'),
    path('imaging-study/<int:pk>/delete/', login_required(ImagingStudyDeleteView.as_view()), name='imaging_study_delete'),
    
    # Consultation URLs
    path('consultations/new/<int:patient_id>/', login_required(ConsultationCreateView.as_view()), name='consultation_create'),
    path('consultations/<int:pk>/update/', login_required(ConsultationUpdateView.as_view()), name='consultation_update'),
    path('consultations/<int:pk>/delete/', login_required(ConsultationDeleteView.as_view()), name='consultation_delete'),
] 