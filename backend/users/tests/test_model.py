from django.contrib.auth import get_user_model
from django.test import TestCase

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
        expected_output = self.user.__str__()
        self.assertTrue(
            expected_output.startswith("User email: john@example.com, created at: ")
        )
        self.assertIn("john@example.com", expected_output)
