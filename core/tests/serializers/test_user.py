from django.test import TestCase
from django.contrib.auth import get_user_model
from core.serializers.user import UserSerializer
from core.forms.user import UserCreationForm
from django.core.exceptions import ValidationError

User = get_user_model()

class UserSerializerTest(TestCase):
    def setUp(self):
        self.test_password = 'test_password_123'  # Common test password
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': self.test_password,
            'password2': self.test_password,
            'role': 'NEUROLOGIST'
        }
        self.user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password=self.test_password,
            role='NEUROLOGIST'
        )

    def test_user_serializer_serialization(self):
        """Test serialization of user data"""
        serializer = UserSerializer(self.user)
        data = serializer.data
        self.assertEqual(data['username'], self.user.username)
        self.assertEqual(data['email'], self.user.email)
        self.assertNotIn('password', data)
        self.assertNotIn('password2', data)

    def test_user_serializer_deserialization(self):
        """Test deserialization of user data"""
        serializer = UserSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, self.user_data['username'])
        self.assertTrue(user.check_password(self.user_data['password']))

    def test_user_serializer_validation(self):
        """Test validation of user data"""
        # Test with missing required fields
        serializer = UserSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
        self.assertIn('email', serializer.errors)

        # Test with invalid email
        data = self.user_data.copy()
        data['email'] = 'invalid-email'
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

        # Test with duplicate username
        data = self.user_data.copy()
        data['username'] = 'existinguser'
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

        # Test with duplicate email
        data = self.user_data.copy()
        data['email'] = 'existing@example.com'
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

        # Test with only password1 provided
        data = self.user_data.copy()
        del data['password2']
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

        # Test with only password2 provided
        data = self.user_data.copy()
        del data['password']
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

        # Test with mismatched passwords
        data = self.user_data.copy()
        data['password2'] = 'different_password'
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_user_serializer_update(self):
        """Test updating user data"""
        data = {
            'username': 'newusername',
            'email': 'new@example.com'
        }
        serializer = UserSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(updated_user.username, data['username'])
        self.assertEqual(updated_user.email, data['email']) 