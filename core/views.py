from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count, Q
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from .models import (
    User, Patient, VitalSign, LabResult, 
    ImagingStudy, NeurologistConsultation, AlertNotification
)
from .serializers import (
    UserSerializer, PatientSerializer, VitalSignSerializer,
    LabResultSerializer, ImagingStudySerializer,
    NeurologistConsultationSerializer, AlertNotificationSerializer
)
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from datetime import timedelta
from .forms import (
    PatientForm, VitalSignForm, LabResultForm, 
    ImagingStudyForm, CustomUserCreationForm, ConsultationForm
)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'core/login.html')

class SignUpView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'core/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully. Please log in.')
        return response

# Create your views here.

class IsMobileTechnician(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.MOBILE_TECHNICIAN

class IsNeurologist(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.NEUROLOGIST

class AlertListView(LoginRequiredMixin, ListView):
    model = AlertNotification
    template_name = 'core/alert_list.html'
    context_object_name = 'alerts'
    ordering = ['-created_at']

    def get_queryset(self):
        return AlertNotification.objects.filter(
            Q(acknowledged_at__isnull=True) | 
            Q(created_at__gte=timezone.now() - timedelta(days=1))
        )

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == User.Role.MOBILE_TECHNICIAN:
            return Patient.objects.filter(created_by=self.request.user)
        return Patient.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        total_patients = Patient.objects.count()
        avg_nihss = Patient.objects.aggregate(avg_nihss=Avg('nihss_score'))['avg_nihss']
        
        # Count patients by stroke type (based on diagnosis)
        stroke_types = Patient.objects.exclude(diagnosis='').values('diagnosis').annotate(
            count=Count('id')
        )

        return Response({
            'total_patients': total_patients,
            'average_nihss_score': round(avg_nihss, 2) if avg_nihss else None,
            'stroke_types': list(stroke_types)
        })

class VitalSignViewSet(viewsets.ModelViewSet):
    queryset = VitalSign.objects.all()
    serializer_class = VitalSignSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)

class LabResultViewSet(viewsets.ModelViewSet):
    queryset = LabResult.objects.all()
    serializer_class = LabResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)

class ImagingStudyViewSet(viewsets.ModelViewSet):
    queryset = ImagingStudy.objects.all()
    serializer_class = ImagingStudySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)

class NeurologistConsultationViewSet(viewsets.ModelViewSet):
    queryset = NeurologistConsultation.objects.all()
    serializer_class = NeurologistConsultationSerializer
    permission_classes = [IsNeurologist]

    def perform_create(self, serializer):
        serializer.save(neurologist=self.request.user)

class AlertNotificationViewSet(viewsets.ModelViewSet):
    queryset = AlertNotification.objects.all()
    serializer_class = AlertNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == User.Role.MOBILE_TECHNICIAN:
            return AlertNotification.objects.filter(created_by=self.request.user)
        return AlertNotification.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        return Response({'status': 'alert acknowledged'})

# Template-based views
@login_required
def dashboard(request):
    # Statistics
    total_patients = Patient.objects.count()
    avg_nihss = Patient.objects.filter(nihss_score__isnull=False).aggregate(
        avg=Avg('nihss_score')
    )['avg'] or 0
    pending_consultations = NeurologistConsultation.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=1)
    ).count()
    critical_alerts = AlertNotification.objects.filter(
        is_critical=True,
        acknowledged_at__isnull=True
    ).count()

    # Recent patients with their latest vitals
    recent_patients = Patient.objects.all().order_by('-created_at')[:5]
    for patient in recent_patients:
        patient.latest_vitals = VitalSign.objects.filter(
            patient=patient
        ).order_by('-recorded_at').first()

    # Critical alerts
    critical_alerts_list = AlertNotification.objects.filter(
        is_critical=True,
        acknowledged_at__isnull=True
    ).order_by('-created_at')[:5]

    context = {
        'total_patients': total_patients,
        'average_nihss': avg_nihss,
        'pending_consultations': pending_consultations,
        'critical_alerts': critical_alerts,
        'recent_patients': recent_patients,
        'critical_alerts_list': critical_alerts_list,
    }
    return render(request, 'core/dashboard.html', context)

class PatientListView(LoginRequiredMixin, ListView):
    model = Patient
    template_name = 'core/patient_list.html'
    context_object_name = 'patients'
    paginate_by = 10
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role == User.Role.MOBILE_TECHNICIAN:
            return queryset.filter(created_by=self.request.user)
        return queryset

class PatientDetailView(LoginRequiredMixin, DetailView):
    model = Patient
    template_name = 'core/patient_detail.html'
    context_object_name = 'patient'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.get_object()
        
        # Get vital signs ordered by recorded_at
        context['vital_signs'] = VitalSign.objects.filter(patient=patient).order_by('-recorded_at')
        
        # Get lab results ordered by recorded_at
        context['lab_results'] = LabResult.objects.filter(patient=patient).order_by('-recorded_at')
        
        # Get imaging studies ordered by recorded_at
        context['imaging_studies'] = ImagingStudy.objects.filter(patient=patient).order_by('-recorded_at')
        
        # Get consultations ordered by created_at
        context['consultations'] = NeurologistConsultation.objects.filter(patient=patient).order_by('-created_at')
        
        # Get alerts ordered by created_at
        context['alerts'] = AlertNotification.objects.filter(patient=patient).order_by('-created_at')
        
        return context

class PatientCreateView(LoginRequiredMixin, CreateView):
    model = Patient
    form_class = PatientForm
    template_name = 'core/patient_form.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Patient created successfully. You can now add vital signs and lab results.')
        return response

    def get_success_url(self):
        return reverse_lazy('patient_detail', kwargs={'pk': self.object.pk})

class ConsultationCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = NeurologistConsultation
    form_class = ConsultationForm
    template_name = 'core/consultation_form.html'
    login_url = 'login'
    permission_denied_message = "Only neurologists can create consultations."

    def test_func(self):
        return self.request.user.role == User.Role.NEUROLOGIST

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect(self.login_url)
        messages.error(self.request, self.permission_denied_message)
        return redirect('patient_detail', pk=self.kwargs.get('patient_id'))

    def form_valid(self, form):
        form.instance.neurologist = self.request.user
        form.instance.patient = get_object_or_404(Patient, pk=self.kwargs.get('patient_id'))
        response = super().form_valid(form)
        messages.success(self.request, 'Consultation created successfully.')
        return response

    def get_success_url(self):
        return reverse_lazy('patient_detail', kwargs={'pk': self.kwargs.get('patient_id')})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            context['patient'] = get_object_or_404(Patient, pk=patient_id)
        return context

class PatientUpdateView(LoginRequiredMixin, UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'core/patient_form.html'
    success_url = reverse_lazy('patient_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Patient updated successfully.')
        return response

@login_required
def alert_acknowledge(request, pk):
    alert = get_object_or_404(AlertNotification, pk=pk)
    if not alert.acknowledged_at:
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        messages.success(request, 'Alert acknowledged successfully.')
    return redirect('dashboard')

class VitalSignCreateView(LoginRequiredMixin, CreateView):
    model = VitalSign
    form_class = VitalSignForm
    template_name = 'core/vital_sign_form.html'
    success_url = reverse_lazy('dashboard')

    def get_initial(self):
        initial = super().get_initial()
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            initial['patient'] = patient_id
        return initial

    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            form.instance.patient = get_object_or_404(Patient, pk=patient_id)
        response = super().form_valid(form)
        messages.success(self.request, 'Vital signs recorded successfully.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            context['patient'] = get_object_or_404(Patient, pk=patient_id)
        return context

class LabResultCreateView(LoginRequiredMixin, CreateView):
    model = LabResult
    form_class = LabResultForm
    template_name = 'core/lab_result_form.html'
    success_url = reverse_lazy('dashboard')

    def get_initial(self):
        initial = super().get_initial()
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            initial['patient'] = patient_id
        return initial

    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            form.instance.patient = get_object_or_404(Patient, pk=patient_id)
        response = super().form_valid(form)
        messages.success(self.request, 'Lab results recorded successfully.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            context['patient'] = get_object_or_404(Patient, pk=patient_id)
        return context

class ImagingStudyCreateView(LoginRequiredMixin, CreateView):
    model = ImagingStudy
    fields = ['study_type', 'findings']
    template_name = 'core/imaging_study_form.html'

    def form_valid(self, form):
        form.instance.patient_id = self.kwargs['patient_id']
        form.instance.recorded_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient_id = self.kwargs['patient_id']
        context['patient'] = get_object_or_404(Patient, pk=patient_id)
        return context

    def get_success_url(self):
        return reverse('patient_detail', kwargs={'pk': self.kwargs['patient_id']})

class VitalSignUpdateView(LoginRequiredMixin, UpdateView):
    model = VitalSign
    form_class = VitalSignForm
    template_name = 'core/vital_sign_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = self.object.patient
        return context

    def get_success_url(self):
        return reverse_lazy('patient_detail', kwargs={'pk': self.object.patient.pk})

class VitalSignDeleteView(LoginRequiredMixin, DeleteView):
    model = VitalSign
    template_name = 'core/confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = self.object.patient
        return context

    def get_success_url(self):
        return reverse_lazy('patient_detail', kwargs={'pk': self.object.patient.pk})

class LabResultUpdateView(LoginRequiredMixin, UpdateView):
    model = LabResult
    form_class = LabResultForm
    template_name = 'core/lab_result_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = self.object.patient
        return context

    def get_success_url(self):
        return reverse_lazy('patient_detail', kwargs={'pk': self.object.patient.pk})

class LabResultDeleteView(LoginRequiredMixin, DeleteView):
    model = LabResult
    template_name = 'core/confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = self.object.patient
        return context

    def get_success_url(self):
        return reverse_lazy('patient_detail', kwargs={'pk': self.object.patient.pk})

class ImagingStudyUpdateView(LoginRequiredMixin, UpdateView):
    model = ImagingStudy
    form_class = ImagingStudyForm
    template_name = 'core/imaging_study_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = self.object.patient
        return context

    def get_success_url(self):
        return reverse_lazy('patient_detail', kwargs={'pk': self.object.patient.pk})

class ImagingStudyDeleteView(LoginRequiredMixin, DeleteView):
    model = ImagingStudy
    template_name = 'core/confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = self.object.patient
        return context

    def get_success_url(self):
        return reverse_lazy('patient_detail', kwargs={'pk': self.object.patient.pk})

class ConsultationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = NeurologistConsultation
    form_class = ConsultationForm
    template_name = 'core/consultation_form.html'

    def test_func(self):
        return self.request.user.role == User.Role.NEUROLOGIST

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = self.object.patient
        return context

    def get_success_url(self):
        return reverse_lazy('patient_detail', kwargs={'pk': self.object.patient.pk})

class ConsultationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = NeurologistConsultation
    template_name = 'core/confirm_delete.html'

    def test_func(self):
        return self.request.user.role == User.Role.NEUROLOGIST

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = self.object.patient
        return context

    def get_success_url(self):
        return reverse_lazy('patient_detail', kwargs={'pk': self.object.patient.pk})
