from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UsersModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="john@example.com",
            password="pass12345",
            first_name="John",
            last_name="Doe",
        )

    def test_get_str_success(self):
        """
        Test __str__ method returns correct string.
        """
        expected_output = "User email: john@example.com, created at: "

        self.assertIn(expected_output, self.user.__str__())