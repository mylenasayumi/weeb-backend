from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


class UsersViewsTest(TestCase):
    def test_index_view_success(self):
        """
        Test simple pour vérifier que la vue d'index des utilisateurs
        est accessible et retourne le contenu attendu.
        """
        response = self.client.get('/api/users/')  # adapté à /api/
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello, world. You're at the users index.")


class UserAPITests(APITestCase):
    def setUp(self):
        """
        Création d'un utilisateur de test pour les tests de l'API.
        """
        self.user = User.objects.create_user(
            email="john@example.com",
            password="pass12345",
            first_name="John",
            last_name="Doe",
        )

    def test_register_user(self):
        """
        Test de l'inscription d'un nouvel utilisateur via l'API.
        Vérifie que l'utilisateur est bien créé et que les données sensibles
        comme le mot de passe ne sont pas incluses dans la réponse.
        """
        url = reverse("user-list")  # POST /api/users/
        payload = {
            "email": "jane@example.com",
            "first_name": "Jane",
            "last_name": "Doe",
            "password": "pass12345",
        }
        res = self.client.post(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", res.data)
        self.assertNotIn("password", res.data)

    def test_jwt_login_and_me(self):
        """
        Test de connexion avec JWT et récupération du profil utilisateur.
        Vérifie que l'utilisateur peut obtenir un token JWT et accéder à son profil via l'endpoint 'me'.
        """
        # Connexion et récupération du token JWT
        token_url = reverse("token_obtain_pair")
        res = self.client.post(
            token_url,
            {"email": "john@example.com", "password": "pass12345"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        access = res.data["access"]

        # Accès au profil utilisateur via l'endpoint 'me'
        me_url = reverse("user-me")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        res = self.client.get(me_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], "john@example.com")

    def test_partial_update_self(self):
        """
        Test que la mise à jour partielle du profil utilisateur est interdite.
        L'utilisateur ne doit pas pouvoir modifier ses propres informations via l'API.
        """
        token_url = reverse("token_obtain_pair")
        access = self.client.post(
            token_url, {"email": "john@example.com", "password": "pass12345"}
        ).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        url = reverse("user-detail", args=[self.user.id])
        res = self.client.patch(url, {"first_name": "Johnny"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
