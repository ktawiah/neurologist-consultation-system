from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models.user import User

class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'role': User.Role.MOBILE_TECHNICIAN
        }

    def test_create_user(self):
        """Test creating a new user"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.role, self.user_data['role'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a new superuser"""
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertEqual(superuser.role, User.Role.MOBILE_TECHNICIAN)

    def test_user_str_representation(self):
        """Test the string representation of a user"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data['username'])

    def test_user_role_choices(self):
        """Test that role choices are correctly defined"""
        choices = User.Role.choices
        self.assertEqual(len(choices), 2)
        self.assertIn(('MT', 'Mobile Technician'), choices)
        self.assertIn(('NR', 'Neurologist'), choices)

    def test_default_role(self):
        """Test that the default role is Mobile Technician"""
        user = User.objects.create_user(
            username='defaultuser',
            email='default@example.com',
            password='testpass123'
        )
        self.assertEqual(user.role, User.Role.MOBILE_TECHNICIAN) 