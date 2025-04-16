from django.test import TestCase
from core.models.user import User
from core.serializers.user import UserSerializer

class UserSerializerTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'role': User.Role.MOBILE_TECHNICIAN
        }
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=User.Role.MOBILE_TECHNICIAN
        )

    def test_user_serializer_serialization(self):
        """Test serializing a user"""
        serializer = UserSerializer(self.user)
        data = serializer.data
        self.assertEqual(data['username'], self.user_data['username'])
        self.assertEqual(data['email'], self.user_data['email'])
        self.assertEqual(data['role'], self.user_data['role'])
        self.assertNotIn('password', data)  # Password should not be included
        self.assertNotIn('password2', data)  # Password2 should not be included

    def test_user_serializer_deserialization(self):
        """Test deserializing user data"""
        # Create new user data to avoid unique constraint issues
        new_user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password2': 'newpass123',
            'role': User.Role.NEUROLOGIST
        }
        serializer = UserSerializer(data=new_user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, new_user_data['username'])
        self.assertEqual(user.email, new_user_data['email'])
        self.assertEqual(user.role, new_user_data['role'])
        self.assertTrue(user.check_password(new_user_data['password']))

    def test_user_serializer_validation(self):
        """Test serializer validation"""
        # Test with missing required fields
        data = {}
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        required_fields = ['username', 'email']
        for field in required_fields:
            self.assertIn(field, serializer.errors)

        # Test with invalid email
        data = self.user_data.copy()
        data['email'] = 'invalid-email'
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

        # Test with duplicate username
        data = self.user_data.copy()
        data['email'] = 'different@example.com'  # Different email to avoid unique constraint
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

        # Test with duplicate email
        data = self.user_data.copy()
        data['username'] = 'differentuser'  # Different username to avoid unique constraint
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

        # Test with only password1 provided
        data = {
            'username': 'newuser1',
            'email': 'new1@example.com',
            'password': 'testpass123'
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
        self.assertEqual(serializer.errors['password'][0], "Both password fields must be provided together.")

        # Test with only password2 provided
        data = {
            'username': 'newuser2',
            'email': 'new2@example.com',
            'password2': 'testpass123'
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
        self.assertEqual(serializer.errors['password'][0], "Both password fields must be provided together.")

        # Test with mismatched passwords
        data = {
            'username': 'newuser3',
            'email': 'new3@example.com',
            'password': 'testpass123',
            'password2': 'differentpass'
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
        self.assertEqual(serializer.errors['password'][0], "Password fields didn't match.")

    def test_user_serializer_update(self):
        """Test updating a user"""
        update_data = {
            'username': 'newusername',
            'email': 'newemail@example.com',
            'role': User.Role.NEUROLOGIST
        }
        serializer = UserSerializer(self.user, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(updated_user.username, update_data['username'])
        self.assertEqual(updated_user.email, update_data['email'])
        self.assertEqual(updated_user.role, update_data['role']) 