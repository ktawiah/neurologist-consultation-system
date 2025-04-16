from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, PatientViewSet, VitalSignViewSet,
    LabResultViewSet, ImagingStudyViewSet,
    NeurologistConsultationViewSet, AlertNotificationViewSet
)

# API Router
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'vital-signs', VitalSignViewSet)
router.register(r'lab-results', LabResultViewSet)
router.register(r'imaging-studies', ImagingStudyViewSet)
router.register(r'consultations', NeurologistConsultationViewSet)
router.register(r'alerts', AlertNotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 