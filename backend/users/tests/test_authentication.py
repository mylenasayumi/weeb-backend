from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from users.serializers import CustomTokenObtainPairSerializer

User = get_user_model()


class CustomTokenObtainPairSerializerTests(APITestCase):
    """
    Tests for the CustomTokenObtainPairSerializer with is_active validation.
    """

    def setUp(self):
        """Create test users with different is_active states."""
        self.active_user = User.objects.create_user(
            email="active@example.com",
            password="pass12345",
            first_name="Active",
            last_name="User",
            is_active=True,
        )

        self.inactive_user = User.objects.create_user(
            email="inactive@example.com",
            password="pass12345",
            first_name="Inactive",
            last_name="User",
            is_active=False,
        )

    def test_serializer_validate_active_user_success(self):
        """
        Test that serializer successfully validates an active user.
        Should return access and refresh tokens.
        """
        data = {
            "email": "active@example.com",
            "password": "pass12345",
        }

        serializer = CustomTokenObtainPairSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertIn("access", serializer.validated_data)
        self.assertIn("refresh", serializer.validated_data)

    def test_serializer_validate_inactive_user_failure(self):
        """
        Test that serializer raises ValidationError for an inactive user.
        Should contain the appropriate error message.
        """
        data = {
            "email": "inactive@example.com",
            "password": "pass12345",
        }

        serializer = CustomTokenObtainPairSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("detail", serializer.errors)
        self.assertIn(
            "not active",
            str(serializer.errors["detail"]).lower(),
        )

    def test_serializer_validate_wrong_password_failure(self):
        """
        Test that serializer raises ValidationError for wrong password.
        Even for active users, wrong credentials should fail.
        """
        data = {
            "email": "active@example.com",
            "password": "wrongpassword",
        }

        serializer = CustomTokenObtainPairSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_serializer_validate_nonexistent_user_failure(self):
        """
        Test that serializer raises ValidationError for non-existent user.
        """
        data = {
            "email": "nonexistent@example.com",
            "password": "pass12345",
        }

        serializer = CustomTokenObtainPairSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_serializer_activate_user_then_validate_success(self):
        """
        Test that a user who becomes active can be validated.
        Simulates an admin activating a user.
        """
        # Initially, user should fail validation
        data = {
            "email": "inactive@example.com",
            "password": "pass12345",
        }

        serializer = CustomTokenObtainPairSerializer(data=data)
        self.assertFalse(serializer.is_valid())

        # Admin activates the user
        self.inactive_user.is_active = True
        self.inactive_user.save()

        # Now validation should succeed
        serializer = CustomTokenObtainPairSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertIn("access", serializer.validated_data)
        self.assertIn("refresh", serializer.validated_data)

    def test_serializer_deactivate_user_then_validate_failure(self):
        """
        Test that a user who becomes inactive can no longer be validated.
        """
        # Initially, user should pass validation
        data = {
            "email": "active@example.com",
            "password": "pass12345",
        }

        serializer = CustomTokenObtainPairSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        # Admin deactivates the user
        self.active_user.is_active = False
        self.active_user.save()

        # Now validation should fail
        serializer = CustomTokenObtainPairSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("detail", serializer.errors)
