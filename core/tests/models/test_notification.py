from django.test import TestCase
from django.utils import timezone
from core.models.user import User
from core.models.patient import Patient
from core.models.notification import AlertNotification

class AlertNotificationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.patient = Patient.objects.create(
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            sex=Patient.Sex.MALE,
            medical_history='No significant medical history',
            chief_complaint='Headache and dizziness',
            nihss_score=5,
            created_by=self.user
        )

    def test_create_alert_notification(self):
        """Test creating an alert notification"""
        alert = AlertNotification.objects.create(
            patient=self.patient,
            alert_type=AlertNotification.AlertType.CRITICAL,
            message='Critical alert test',
            is_critical=True,
            created_by=self.user
        )
        self.assertEqual(alert.patient, self.patient)
        self.assertEqual(alert.alert_type, AlertNotification.AlertType.CRITICAL)
        self.assertEqual(alert.message, 'Critical alert test')
        self.assertTrue(alert.is_critical)
        self.assertEqual(alert.created_by, self.user)
        self.assertIsNone(alert.acknowledged_by)
        self.assertIsNone(alert.acknowledged_at)

    def test_alert_notification_str_representation(self):
        """Test the string representation of an alert notification"""
        alert = AlertNotification.objects.create(
            patient=self.patient,
            alert_type=AlertNotification.AlertType.CRITICAL,
            message='Critical alert test',
            is_critical=True,
            created_by=self.user
        )
        self.assertEqual(str(alert), f"{alert.alert_type} - {alert.message}")

    def test_alert_type_choices(self):
        """Test that alert type choices are correctly defined"""
        choices = AlertNotification.AlertType.choices
        self.assertEqual(len(choices), 3)
        self.assertIn(('CR', 'Critical'), choices)
        self.assertIn(('WR', 'Warning'), choices)
        self.assertIn(('IN', 'Information'), choices)

    def test_mark_as_read(self):
        """Test marking an alert as read"""
        alert = AlertNotification.objects.create(
            patient=self.patient,
            alert_type=AlertNotification.AlertType.CRITICAL,
            message='Critical alert test',
            is_critical=True,
            created_by=self.user
        )
        alert.acknowledged_by = self.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        self.assertEqual(alert.acknowledged_by, self.user)
        self.assertIsNotNone(alert.acknowledged_at)

    def test_alert_ordering(self):
        """Test that alerts are ordered by creation date"""
        alert1 = AlertNotification.objects.create(
            patient=self.patient,
            alert_type=AlertNotification.AlertType.CRITICAL,
            message='First alert',
            is_critical=True,
            created_by=self.user
        )
        alert2 = AlertNotification.objects.create(
            patient=self.patient,
            alert_type=AlertNotification.AlertType.WARNING,
            message='Second alert',
            created_by=self.user
        )
        alerts = list(AlertNotification.objects.all())
        self.assertEqual(alerts[0], alert2)  # Most recent first
        self.assertEqual(alerts[1], alert1) 