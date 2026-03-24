from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

User = get_user_model()
import pytest

pytestmark = pytest.mark.django_db


def test_create_user_success(api_client):
    """
    Should create a new user from the given data.
    """
    # ARRANGE
    url = reverse("users-list")
    payload = {
        "email": "jane@example.com",
        "first_name": "Jane",
        "last_name": "Doe",
        "password": "pass12345",
    }

    # ACT
    res = api_client.post(url, payload, format="json")

    # ASSERT
    assert res.status_code == status.HTTP_201_CREATED
    assert payload["email"] in res.data["email"]
    assert "password" not in res.data


def test_create_user_same_email_failure(user, api_client):
    """
    Should not create a second user from the same data.
    """
    # ARRANGE
    url = reverse("users-list")
    expected_output = {"email": ["user with this email already exists."]}
    payload = {
        "email": "john@example.com",
        "first_name": "Jon",
        "last_name": "Doe",
        "password": "pass12345",
    }

    # ACT
    res = api_client.post(url, payload, format="json")

    # ASSERT
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.json() == expected_output


def test_create_user_no_first_name_failure(api_client):
    """
    Should not create a user without a first name.
    """
    # ARRANGE
    url = reverse("users-list")
    expected_output = {"first_name": ["This field may not be blank."]}
    payload = {
        "email": "other@example.com",
        "first_name": "",
        "last_name": "Doe",
        "password": "pass12345",
    }

    # ACT
    res = api_client.post(url, payload, format="json")

    # ASSERT
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.json() == expected_output


def test_create_user_no_last_name_failure(api_client):
    """
    Should not create a user without a first name.
    """
    # ARRANGE
    url = reverse("users-list")
    expected_output = {"last_name": ["This field may not be blank."]}
    payload = {
        "email": "other@example.com",
        "first_name": "Jane",
        "last_name": "",
        "password": "pass12345",
    }

    # ACT
    res = api_client.post(url, payload, format="json")

    # ASSERT
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.json() == expected_output


def test_create_user_no_password_failure(api_client):
    """
    Should not create a user without a password.
    """
    # ARRANGE
    url = reverse("users-list")
    expected_output = {"password": ["This field may not be blank."]}
    payload = {
        "email": "other@example.com",
        "first_name": "Jane",
        "last_name": "Doe",
        "password": "",
    }

    # ACT
    res = api_client.post(url, payload, format="json")

    # ASSERT
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.json() == expected_output


def test_get_tokens_success(api_client, user):
    """
    Should return access and refresh in response.
    """
    # ARRANGE
    url = reverse("token_obtain_pair")
    data = {"email": "john@example.com", "password": "pass12345"}
    user.is_active = True
    user.save()

    # ACT
    res = api_client.post(url, data=data)

    # ASSERT
    assert res.status_code == status.HTTP_200_OK
    assert "access" in res.json()
    assert "refresh" in res.json()


def test_get_tokens_bad_email_failure(api_client):
    """
    Should return access and refresh in response.
    """
    # ARRANGE
    url = reverse("token_obtain_pair")
    data = {"email": "bad_email@example.com", "password": "pass12345"}
    expected_output = {"detail": "No active account found with the given credentials"}

    # ACT
    res = api_client.post(url, data=data)

    # ASSERT
    assert res.status_code == status.HTTP_401_UNAUTHORIZED
    assert res.json() == expected_output


def test_get_tokens_bad_pwd_failure(api_client):
    """
    Should not return access and refresh if a bad password is given.
    """
    # ARRANGE
    url = reverse("token_obtain_pair")
    data = {"email": "john@example.com", "password": "BAD_PASSWORD"}
    expected_output = {"detail": "No active account found with the given credentials"}

    # ACT
    res = api_client.post(url, data)

    # ASSERT
    assert res.status_code == status.HTTP_401_UNAUTHORIZED
    assert res.json() == expected_output


def test_get_me_url_success(api_client, user):
    """
    Should access the endpoit me if logged in.
    """
    # ARRANGE
    url = reverse("token_obtain_pair")
    data = {"email": "john@example.com", "password": "pass12345"}
    user.is_active = True
    user.save()

    # ACT
    res = api_client.post(url, data=data)

    access = res.data["access"]

    url = reverse("users-me")

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    res = api_client.get(url)

    # ASSERT
    assert res.status_code == status.HTTP_200_OK
    assert res.data["email"] == "john@example.com"


def test_user_update_failure(authenticated_client, user):
    """
    Should not allow a user to update himself.
    """
    # ARRANGE
    url = reverse("users-detail", args=[user.id])
    data = {"first_name": "James"}
    expected_output = {"detail": "You do not have permission to perform this action."}

    # ACT
    res = authenticated_client.patch(url, data)

    # ASSERT
    assert res.status_code == status.HTTP_403_FORBIDDEN
    assert res.json() == expected_output


def test_admin_update_success(user, authenticated_client):
    """
    Should allow admin to update a user.
    """
    # ARRANGE
    admin = User.objects.create_superuser(
        email="admin@example.com",
        password="admin12356",
        first_name="admin",
        last_name="admin",
    )
    url = reverse("users-detail", args=[user.id])
    authenticated_client.force_authenticate(user=admin)

    # ACT
    response = authenticated_client.patch(url, {"first_name": "Updated"})

    # ASSERT
    assert response.status_code == status.HTTP_200_OK
    assert response.data["first_name"] == "Updated"
    assert "password" not in response.data


def test_get_UserSerializer_success(user, authenticated_client):
    """
    Should ensure the correct serializer is used depending on the action (create vs list).
    """
    # ARRANGE
    url = reverse("users-list")

    # ACT
    response = authenticated_client.get(url)

    # ASSERT
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 1
    assert "email" in response.data["results"][0]


# class UsersAPITests(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             email="john@example.com",
#             password="pass12345",
#             first_name="John",
#             last_name="Doe",
#         )
#         self.client = APIClient()

#     # def test_create_user_success(self):
#     #     """
#     #     Test successful user registration
#     #         should not return a password
#     #     """
#     #     url = reverse("users-list")  # POST /api/users/
#     #     payload = {
#     #         "email": "jane@example.com",
#     #         "first_name": "Jane",
#     #         "last_name": "Doe",
#     #         "password": "pass12345",
#     #     }

#     #     res = self.client.post(url, payload, format="json")

#     #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#     #     self.assertIn(payload["email"], res.data["email"])
#     #     self.assertNotIn("password", res.data)

#     # def test_create_user_same_email_failure(self):
#     #     url = reverse("users-list")  # POST /api/users/
#     #     expected_output = {"email": ["user with this email already exists."]}
#     #     payload = {
#     #         "email": "john@example.com",
#     #         "first_name": "Jon",
#     #         "last_name": "Doe",
#     #         "password": "pass12345",
#     #     }

#     #     res = self.client.post(url, payload, format="json")

#     #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
#     #     self.assertEqual(res.json(), expected_output)

#     # def test_create_user_no_first_name_failure(self):
#     #     url = reverse("users-list")  # POST /api/users/
#     #     expected_output = {"first_name": ["This field may not be blank."]}

#     #     payload = {
#     #         "email": "other@example.com",
#     #         "first_name": "",
#     #         "last_name": "Doe",
#     #         "password": "pass12345",
#     #     }
#     #     res = self.client.post(url, payload, format="json")

#     #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
#     #     self.assertEqual(res.json(), expected_output)

#     # def test_create_user_no_last_name_failure(self):
#     #     url = reverse("users-list")  # POST /api/users/
#     #     expected_output = {"last_name": ["This field may not be blank."]}

#     #     payload = {
#     #         "email": "other@example.com",
#     #         "first_name": "Jane",
#     #         "last_name": "",
#     #         "password": "pass12345",
#     #     }
#     #     res = self.client.post(url, payload, format="json")

#     #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
#     #     self.assertEqual(res.json(), expected_output)

#     # def test_create_user_no_password_failure(self):
#     #     url = reverse("users-list")  # POST /api/users/
#     #     expected_output = {"password": ["This field may not be blank."]}

#     #     payload = {
#     #         "email": "other@example.com",
#     #         "first_name": "Jane",
#     #         "last_name": "Doe",
#     #         "password": "",
#     #     }
#     #     res = self.client.post(url, payload, format="json")

#     #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
#     #     self.assertEqual(res.json(), expected_output)

#     # def test_get_tokens_success(self):
#     #     """
#     #     Test successful, response should have access and refresh
#     #     """
#     #     url = reverse("token_obtain_pair")
#     #     self.user.is_active = True
#     #     self.user.save()

#     #     res = self.client.post(
#     #         url, {"email": "john@example.com", "password": "pass12345"}
#     #     )

#     #     self.assertEqual(res.status_code, status.HTTP_200_OK)
#     #     self.assertIn("access", res.json())
#     #     self.assertIn("refresh", res.json())

#     # def test_get_tokens_bad_email_failure(self):
#     #     url = reverse("token_obtain_pair")
#     #     expected_output = {
#     #         "detail": "No active account found with the given credentials"
#     #     }

#     #     res = self.client.post(
#     #         url, {"email": "bad_email@example.com", "password": "pass12345"}
#     #     )

#     #     self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
#     #     self.assertEqual(res.json(), expected_output)

#     # def test_get_tokens_bad_pwd_failure(self):
#     #     """
#     #     Test de connexion avec JWT et récupération du profil utilisateur.
#     #     Vérifie que l'utilisateur peut obtenir un token JWT et accéder à son profil via l'endpoint 'me'.
#     #     """
#     #     # Connexion et récupération du token JWT
#     #     url = reverse("token_obtain_pair")
#     #     expected_output = {
#     #         "detail": "No active account found with the given credentials"
#     #     }

#     #     res = self.client.post(
#     #         url, {"email": "john@example.com", "password": "BAD_PASSWORD"}
#     #     )

#     #     self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
#     #     self.assertEqual(res.json(), expected_output)

#     # def test_get_me_url_success(self):
#     #     """
#     #     Test get me endpoint.
#     #     """
#     #     url = reverse("token_obtain_pair")
#     #     self.user.is_active = True
#     #     self.user.save()

#     #     res = self.client.post(
#     #         url, {"email": "john@example.com", "password": "pass12345"}
#     #     )

#     #     access = res.data["access"]

#     #     url = reverse("users-me")

#     #     self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
#     #     res = self.client.get(url)

#     #     self.assertEqual(res.status_code, status.HTTP_200_OK)
#     #     self.assertEqual(res.data["email"], "john@example.com")

#     # def test_user_update_failure(self):
#     #     url = reverse("users-detail", args=[self.user.id])
#     #     expected_output = {
#     #         "detail": "You do not have permission to perform this action."
#     #     }

#     #     self.client.force_authenticate(user=self.user)
#     #     res = self.client.patch(url, {"first_name": "James"})

#     #     self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
#     #     self.assertEqual(res.json(), expected_output)

#     # def test_admin_update_success(self):
#     #     url = reverse("users-detail", args=[self.user.id])
#     #     admin = User.objects.create_superuser(
#     #         email="admin@example.com",
#     #         password="admin12356",
#     #         first_name="admin",
#     #         last_name="admin",
#     #     )

#     #     self.client.force_authenticate(user=admin)
#     #     res = self.client.patch(url, {"first_name": "Updated"})

#     #     self.assertEqual(res.status_code, status.HTTP_200_OK)
#     #     self.assertEqual(res.data["first_name"], "Updated")
#     #     self.assertNotIn("password", res.data)

#     # def test_get_UserSerializer_success(self):
#     #     """
#     #     Ensure the correct serializer is used depending on the action (create vs list).
#     #     """
#     #     url = reverse("users-list")
#     #     res = self.client.get(url)

#     #     self.assertEqual(res.status_code, status.HTTP_200_OK)
#     #     self.assertEqual(res.json()["count"], 1)
#     #     self.assertIn("email", res.data["results"][0])
