from django.contrib.auth import get_user_model
from django.test import TestCase


User = get_user_model()

class EmailUserManagerTest(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_create_user_success(self):
        user = self.User.objects.create_user(
            email="john@example.com",
            password="pass12345",
            first_name="John",
            last_name="Doe"
        )
        self.assertEqual(user.email, "john@example.com")
        self.assertTrue(user.check_password("pass12345"))
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")

    def test_create_user_no_email_failure(self):
        expected_output = "Email is required"

        with self.assertRaises(ValueError) as err:
            self.User.objects.create_user(
                email="",
                password="pass12345",
                first_name="John",
                last_name="Doe"
            )

        self.assertEqual(str(err.exception), expected_output)

    def test_create_user_no_pwd_failure(self):
        expected_output = "Password is required"

        with self.assertRaises(ValueError) as err:
            self.User.objects.create_user(
                email="john@example.com",
                password="",
                first_name="John",
                last_name="Doe"
            )

        self.assertEqual(str(err.exception), expected_output)

    def test_create_user_no_first_name_failure(self):
        expected_output = "First name is required"

        with self.assertRaises(ValueError) as err:
            self.User.objects.create_user(
                email="john@example.com",
                password="pass12345",
                first_name="",
                last_name="Doe"
            )

        self.assertEqual(str(err.exception), expected_output)

    def test_create_user_no_last_name_failure(self):
        expected_output = "Last name is required"

        with self.assertRaises(ValueError) as err:
            self.User.objects.create_user(
                email="john@example.com",
                password="pass12345",
                first_name="John",
                last_name=""
            )

        self.assertEqual(str(err.exception), expected_output)

    def test_create_superuser_success(self):
        superuser = self.User.objects.create_superuser(
            email="admin@example.com",
            password="pass12345",
            first_name="John",
            last_name="Doe"
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)
        self.assertEqual(superuser.email, "admin@example.com")

    def test_create_superuser_not_staff_failure(self):
        expected_output = "Superuser must have is_staff=True."

        with self.assertRaises(ValueError) as cm:
            self.User.objects.create_superuser(
                email="admin@example.com",
                password="adminpass",
                first_name="Admin",
                last_name="User",
                is_staff=False
            )
        self.assertEqual(str(cm.exception), expected_output)

    def test_create_superuser_not_super_failure(self):
        expected_output = "Superuser must have is_superuser=True."

        with self.assertRaises(ValueError) as cm:
            self.User.objects.create_superuser(
                email="admin@example.com",
                password="adminpass",
                first_name="Admin",
                last_name="User",
                is_superuser=False
            )
        self.assertEqual(str(cm.exception), expected_output)
