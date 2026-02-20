from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class UsersAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="john@example.com",
            password="pass12345",
            first_name="John",
            last_name="Doe",
        )
        self.client = APIClient()

    def test_create_user_success(self):
        """
        Test successful user registration
            should not return a password
        """
        url = reverse("users-list")  # POST /api/users/
        payload = {
            "email": "jane@example.com",
            "first_name": "Jane",
            "last_name": "Doe",
            "password": "pass12345",
        }

        res = self.client.post(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn(payload["email"], res.data["email"])
        self.assertNotIn("password", res.data)

    def test_create_user_same_email_failure(self):
        url = reverse("users-list")  # POST /api/users/
        expected_output = {"email": ["user with this email already exists."]}
        payload = {
            "email": "john@example.com",
            "first_name": "Jon",
            "last_name": "Doe",
            "password": "pass12345",
        }

        res = self.client.post(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.json(), expected_output)

    def test_create_user_no_first_name_failure(self):
        url = reverse("users-list")  # POST /api/users/
        expected_output = {"first_name": ["This field may not be blank."]}

        payload = {
            "email": "other@example.com",
            "first_name": "",
            "last_name": "Doe",
            "password": "pass12345",
        }
        res = self.client.post(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.json(), expected_output)

    def test_create_user_no_last_name_failure(self):
        url = reverse("users-list")  # POST /api/users/
        expected_output = {"last_name": ["This field may not be blank."]}

        payload = {
            "email": "other@example.com",
            "first_name": "Jane",
            "last_name": "",
            "password": "pass12345",
        }
        res = self.client.post(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.json(), expected_output)

    def test_create_user_no_password_failure(self):
        url = reverse("users-list")  # POST /api/users/
        expected_output = {"password": ["This field may not be blank."]}

        payload = {
            "email": "other@example.com",
            "first_name": "Jane",
            "last_name": "Doe",
            "password": "",
        }
        res = self.client.post(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.json(), expected_output)

    def test_get_tokens_success(self):
        """
        Test successful, response should have access and refresh
        """
        url = reverse("token_obtain_pair")
        self.user.is_active = True
        self.user.save()

        res = self.client.post(
            url, {"email": "john@example.com", "password": "pass12345"}
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.json())
        self.assertIn("refresh", res.json())

    def test_get_tokens_bad_email_failure(self):
        url = reverse("token_obtain_pair")
        expected_output = {
            "detail": "No active account found with the given credentials"
        }

        res = self.client.post(
            url, {"email": "bad_email@example.com", "password": "pass12345"}
        )

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res.json(), expected_output)

    def test_get_tokens_bad_pwd_failure(self):
        """
        Test de connexion avec JWT et récupération du profil utilisateur.
        Vérifie que l'utilisateur peut obtenir un token JWT et accéder à son profil via l'endpoint 'me'.
        """
        # Connexion et récupération du token JWT
        url = reverse("token_obtain_pair")
        expected_output = {
            "detail": "No active account found with the given credentials"
        }

        res = self.client.post(
            url, {"email": "john@example.com", "password": "BAD_PASSWORD"}
        )

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res.json(), expected_output)

    def test_get_me_url_success(self):
        """
        Test get me endpoint.
        """
        url = reverse("token_obtain_pair")
        self.user.is_active = True
        self.user.save()

        res = self.client.post(
            url, {"email": "john@example.com", "password": "pass12345"}
        )

        access = res.data["access"]

        url = reverse("users-me")

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], "john@example.com")

    def test_user_update_failure(self):
        url = reverse("users-detail", args=[self.user.id])
        expected_output = {
            "detail": "You do not have permission to perform this action."
        }

        self.client.force_authenticate(user=self.user)
        res = self.client.patch(url, {"first_name": "James"})

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.json(), expected_output)

    def test_admin_update_success(self):
        url = reverse("users-detail", args=[self.user.id])
        admin = User.objects.create_superuser(
            email="admin@example.com",
            password="admin12356",
            first_name="admin",
            last_name="admin",
        )

        self.client.force_authenticate(user=admin)
        res = self.client.patch(url, {"first_name": "Updated"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["first_name"], "Updated")
        self.assertNotIn("password", res.data)

    def test_get_UserSerializer_success(self):
        """
        Ensure the correct serializer is used depending on the action (create vs list).
        """
        url = reverse("users-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()["count"], 1)
        self.assertIn("email", res.data["results"][0])

    def test_password_reset_request_success(self):
        """
        Test that a password reset request returns a generic success message and prints the reset link with the correct frontend_url.
        """
        url = reverse("password_reset_request")
        payload = {
            "email": "john@example.com",
            "frontend_url": "http://testfrontend.com",
        }

        with self.assertLogs(level="INFO") as log:
            res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(
            "If an account is associated with this email", res.json()["message"]
        )

    def test_password_reset_request_nonexistent_email(self):
        """
        Test that a password reset request for a nonexistent email still returns a generic success message.
        """
        url = reverse("password_reset_request")
        payload = {
            "email": "doesnotexist@example.com",
            "frontend_url": "http://testfrontend.com",
        }

        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(
            "If an account is associated with this email", res.json()["message"]
        )

    def test_password_reset_confirm_success(self):
        """
        Test that a valid token and uidb64 allow password reset.
        """
        # Generate token for the user
        uidb64 = urlsafe_base64_encode(smart_bytes(self.user.id))
        token = PasswordResetTokenGenerator().make_token(self.user)
        url = reverse("password_reset_confirm") + f"?uidb64={uidb64}"
        payload = {"token": token, "password": "newpass12345"}

        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("Password reset successfully", res.json()["message"])

        # Check that the password was actually changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass12345"))

    def test_password_reset_confirm_invalid_token(self):
        """
        Test that an invalid token does not allow password reset.
        """
        uidb64 = urlsafe_base64_encode(smart_bytes(self.user.id))
        url = reverse("password_reset_confirm") + f"?uidb64={uidb64}"
        payload = {"token": "invalidtoken", "password": "newpass12345"}

        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid or expired token", res.json()["error"])

    def test_password_reset_confirm_uidb64_token_mismatch(self):
        """
        Test that a valid token for one user cannot be used with another user's uidb64.
        """
        # Create a second user
        user2 = User.objects.create_user(
            email="jane@example.com",
            password="pass12345",
            first_name="Jane",
            last_name="Doe",
        )

        # Generate token for user1
        token = PasswordResetTokenGenerator().make_token(self.user)
        # Use user2's uidb64
        uidb64 = urlsafe_base64_encode(smart_bytes(user2.id))
        url = reverse("password_reset_confirm") + f"?uidb64={uidb64}"
        payload = {"token": token, "password": "newpass12345"}

        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid or expired token", res.json()["error"])
