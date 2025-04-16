from django.test import TestCase
from django.core.exceptions import ValidationError
from core.forms.user import UserCreationForm, UserChangeForm
from core.models.user import User

class UserFormsTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'role': User.Role.MOBILE_TECHNICIAN
        }

    def test_user_creation_form_valid(self):
        """Test that the user creation form works with valid data"""
        form = UserCreationForm(data=self.user_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.role, self.user_data['role'])
        self.assertTrue(user.check_password(self.user_data['password1']))

    def test_user_creation_form_password_mismatch(self):
        """Test that the form validates password matching"""
        data = self.user_data.copy()
        data['password2'] = 'differentpassword'
        form = UserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_user_creation_form_required_fields(self):
        """Test that required fields are properly validated"""
        form = UserCreationForm(data={})
        self.assertFalse(form.is_valid())
        required_fields = ['username', 'email', 'password1', 'password2']
        for field in required_fields:
            self.assertIn(field, form.errors)

    def test_user_change_form(self):
        """Test that the user change form works correctly"""
        user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        form_data = {
            'username': 'newusername',
            'email': 'newemail@example.com',
            'role': User.Role.NEUROLOGIST
        }
        form = UserChangeForm(data=form_data, instance=user)
        self.assertTrue(form.is_valid())
        updated_user = form.save()
        self.assertEqual(updated_user.username, form_data['username'])
        self.assertEqual(updated_user.email, form_data['email'])
        self.assertEqual(updated_user.role, form_data['role'])

    def test_user_creation_form_unique_username(self):
        """Test that the form validates unique usernames"""
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        data = self.user_data.copy()
        data['username'] = 'existinguser'
        form = UserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_user_creation_form_unique_email(self):
        """Test that the form validates unique emails"""
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        data = self.user_data.copy()
        data['email'] = 'existing@example.com'
        form = UserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors) 