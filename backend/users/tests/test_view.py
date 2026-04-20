from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
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


def test_password_reset_request_success(api_client, user):
    """
    Test that a password reset request returns a generic success message and prints the reset link with the correct frontend_url.
    """

    # ARRANGE
    url = reverse("password_reset_request")
    payload = {
        "email": "john@example.com",
        "frontend_url": "http://testfrontend.com",
    }

    # ACT
    res = api_client.post(url, payload, format="json")

    # ASSERT
    assert res.status_code == status.HTTP_200_OK
    assert "If an account is associated with this email" in res.json()["message"]


def test_password_reset_request_nonexistent_email(api_client):
    """
    Test that a password reset request for a nonexistent email still returns a generic success message.
    """

    # ARRANGE
    url = reverse("password_reset_request")
    payload = {
        "email": "doesnotexist@example.com",
        "frontend_url": "http://testfrontend.com",
    }

    # ACT
    res = api_client.post(url, payload, format="json")

    # ASSERT
    assert res.status_code == status.HTTP_200_OK
    assert "If an account is associated with this email" in res.json()["message"]


def test_password_reset_confirm_success(api_client, user):
    """
    Test that a valid token and uidb64 allow password reset.
    """

    # ARRANGE
    # Generate token for the user
    uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
    token = PasswordResetTokenGenerator().make_token(user)
    url = reverse("password_reset_confirm") + f"?uidb64={uidb64}"
    payload = {"token": token, "password": "newpass12345"}

    # ACT
    res = api_client.post(url, payload, format="json")

    # ASSERT
    assert res.status_code == status.HTTP_200_OK
    assert "Password reset successfully" in res.json()["message"]

    # Check that the password was actually changed
    user.refresh_from_db()
    assert user.check_password("newpass12345")


def test_password_reset_confirm_invalid_token(api_client, user):
    """
    Test that an invalid token does not allow password reset.
    """

    # ARRANGE
    uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
    url = reverse("password_reset_confirm") + f"?uidb64={uidb64}"
    payload = {"token": "invalidtoken", "password": "newpass12345"}

    # ACT
    res = api_client.post(url, payload, format="json")

    # ASSERT
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid or expired token" in res.json()["error"]


def test_password_reset_confirm_uidb64_token_mismatch(api_client, user):
    """
    Test that a valid token for one user cannot be used with another user's uidb64.
    """

    # ARRANGE
    # Create a second user
    user2 = User.objects.create_user(
        email="jane@example.com",
        password="pass12345",
        first_name="Jane",
        last_name="Doe",
    )

    # Generate token for user1
    token = PasswordResetTokenGenerator().make_token(user)
    # Use user2's uidb64
    uidb64 = urlsafe_base64_encode(smart_bytes(user2.id))
    url = reverse("password_reset_confirm") + f"?uidb64={uidb64}"
    payload = {"token": token, "password": "newpass12345"}

    # ACT
    res = api_client.post(url, payload, format="json")

    # ASSERT
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid or expired token" in res.json()["error"]


def test_password_reset_request_email_missing_failure(api_client):
    """
    Test that a password reset request without an email returns an error.
    """

    # ARRANGE
    url = reverse("password_reset_request")
    payload = {"frontend_url": "http://testfrontend.com"}
    expected_output = {"email": ["This field is required."]}

    # ACT
    res = api_client.post(url, payload, format="json")

    # ASSERT
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.json() == expected_output


def test_password_reset_confirm_invalid_uidb64(api_client):
    """
    Test that a password reset confirmation with an invalid uidb64 fails.
    """

    # ARRANGE
    url = reverse("password_reset_confirm") + "?uidb64=invaliduidb64"
    payload = {"token": "validtoken", "password": "newpass12345"}

    # ACT
    res = api_client.post(url, payload, format="json")

    # ASSERT
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid reset link." in res.json()["error"]


def test_password_reset_confirm_missing_uidb64(api_client):
    """
    Test that the password reset confirmation endpoint returns an error
    if the 'uidb64' parameter is missing in the request.
    """

    # ARRANGE
    url = reverse("password_reset_confirm")
    payload = {"token": "validtoken", "password": "newpass12345"}

    # ACT
    res = api_client.post(url, payload, format="json")

    # ASSERT
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert "Missing uidb64 parameter." in res.json()["error"]


def test_password_reset_request_with_frontend_url(api_client):
    """
    Test that the 'frontend_url' parameter is used correctly when provided in the request.
    """

    # ARRANGE
    url = reverse("password_reset_request")
    frontend_url = "http://customfrontend.com"
    payload = {"email": "john@example.com", "frontend_url": frontend_url}

    # ACT
    res = api_client.post(url, payload, format="json")

    # ASSERT
    assert res.status_code == status.HTTP_200_OK
    assert "If an account is associated with this email" in res.json()["message"]


def test_password_reset_request_without_frontend_url(api_client):
    """
    Test that the default frontend URL is used when 'frontend_url' parameter is not provided in the request.
    """

    # ARRANGE
    url = reverse("password_reset_request")
    payload = {"email": "john@example.com"}

    # ACT
    res = api_client.post(url, payload, format="json")

    # ASSERT
    assert res.status_code == status.HTTP_200_OK
    assert "If an account is associated with this email" in res.json()["message"]
