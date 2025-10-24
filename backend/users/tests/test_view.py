from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory, APITestCase
from users.views import IsSelf

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
        url = reverse("token_obtain_pair")
        res = self.client.post(
            url, {"email": "john@example.com", "password": "pass12345"}
        )

        access = res.data["access"]

        url = reverse("users-me")

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], "john@example.com")

    def test_get_other_user_failure(self):
        """
        Failure: test that a user cannot access another user's data.
        """
        user2 = User.objects.create_user(
            email="u2@example.com", password="123", first_name="C", last_name="D"
        )

        # Create fake request
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = self.user

        # Initiatlize our custom permission
        permission = IsSelf()

        self.assertFalse(permission.has_object_permission(request, None, user2))
        self.assertTrue(permission.has_object_permission(request, None, self.user))

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
