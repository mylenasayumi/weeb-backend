from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken

User = get_user_model()

# Indicate to pytest that it needs access to db
pytestmark = pytest.mark.django_db


def test_logout_view_deletes_tokens_success(authenticated_client):
    """
    Should delete access and refresh token cookies on logout.
    """
    # ARRANGE
    url = reverse("logout")

    # ACT
    response = authenticated_client.post(url)

    # ASSERT
    assert response.status_code == 200
    assert response.data["detail"] == "Déconnecté."

    cookies = response.cookies
    assert "refresh_token" in cookies


def test_refresh_token_missing_failure(api_client):
    """
    Should return 401 if refresh token cookie is missing.
    """
    # ARRANGE
    url = reverse("token_refresh")

    # ACT
    response = api_client.post(url)

    # ASSERT
    assert response.status_code == 401
    assert response.data["detail"] == "Refresh token manquant."


@patch("backend.views.TokenRefreshView.post")
def test_refresh_token_invalid_failure(mock_super_post, api_client):
    """
    Should return 401 when refresh token is invalid.
    """
    # ARRANGE
    url = reverse("token_refresh")

    mock_super_post.side_effect = InvalidToken("Token invalide")

    api_client.cookies["refresh_token"] = "bad_refresh_token"

    # ACT
    response = api_client.post(url)

    # ASSERT
    assert response.status_code == 401


@patch("backend.views.TokenRefreshView.post")
def test_refresh_token_success(mock_super_post, api_client):
    """
    Should refresh token and reset refresh_token cookie.
    """
    # ARRANGE
    url = reverse("token_refresh")

    mock_response = Response(
        {
            "refresh": "new_refresh_token",
        }
    )

    mock_super_post.return_value = mock_response

    api_client.cookies["refresh_token"] = "old_refresh_token"

    # ACT
    response = api_client.post(url)

    # ASSERT
    assert response.status_code == 200
    assert "refresh_token" in response.cookies


def test_redirect_to_github_success(api_client, settings):
    """
    Should redirect to github with right params.
    """
    # ARRANGE
    settings.GITHUB_CLIENT_ID = "fake_client_id"
    settings.GITHUB_CALLBACK_URL = "http://localhost:8000/api/auth/github/callback/"
    url = reverse("github_login")

    # ACT
    response = api_client.get(url)

    # ASSERT
    assert response.status_code == 302
    assert "https://github.com/login/oauth/authorize" in response["Location"]
    assert "fake_client_id" in response["Location"]
    assert "user:email" in response["Location"]


def test_redirect_contains_callback_url_success(api_client, settings):
    """
    Should contains properly the complete url.
    """
    # ARRANGE
    settings.GITHUB_CLIENT_ID = "fake_client_id"
    settings.GITHUB_CALLBACK_URL = "http://localhost:8000/api/auth/github/callback/"
    url = reverse("github_login")

    # ACT
    response = api_client.get(url)

    # ASSERT
    assert "redirect_uri" in response["Location"]


# def test_no_code_redirects_failure(api_client, settings):
#     """
#     Should return no_code if no code il url.
#     """
#     # ARRANGE
#     settings.FRONTEND_URL = "http://localhost:3000"
#     url = reverse("github_callback")

#     session = api_client.session
#     session["github_oauth_state"] = "test_state"
#     session.save()

#     # ACT
#     response = api_client.get(url, {"state": "test_state"})

#     # ASSERT
#     assert response.status_code == 302
#     assert "error=no_code" in response["Location"]


# @patch("backend.views.requests.post")
# def test_invalid_github_token_redirects_failure(mock_post, api_client, settings):
#     """
#     Should return an error if github return no token.
#     """
#     # ARRAGE
#     settings.FRONTEND_URL = "http://localhost:3000"
#     settings.GITHUB_CLIENT_ID = "fake_client_id"
#     settings.GITHUB_CLIENT_SECRET = "fake_secret"
#     settings.GITHUB_CALLBACK_URL = "http://localhost:8000/api/auth/github/callback/"
#     url = reverse("github_callback")

#     session = api_client.session
#     session["github_oauth_state"] = "test_state"
#     session.save()

#     mock_post.return_value = MagicMock(json=lambda: {"error": "bad_verification_code"})

#     # ACT
#     response = api_client.get(url, {"code": "invalid_code", "state": "test_state"})

#     # ASSERT
#     assert response.status_code == 302
#     assert "error=token_failed" in response["Location"]


# @patch("backend.views.requests.get")
# @patch("backend.views.requests.post")
# def test_no_email_redirects_failure(mock_post, mock_get, api_client, settings):
#     """
#     Should return an error if no email is found.
#     """
#     # ARRANGE
#     settings.FRONTEND_URL = "http://localhost:3000"
#     settings.GITHUB_CLIENT_ID = "fake_client_id"
#     settings.GITHUB_CLIENT_SECRET = "fake_secret"
#     settings.GITHUB_CALLBACK_URL = "http://localhost:8000/api/auth/github/callback/"
#     url = reverse("github_callback")

#     session = api_client.session
#     session["github_oauth_state"] = "test_state"
#     session.save()

#     mock_post.return_value = MagicMock(json=lambda: {"access_token": "fake_token"})

#     # First email empty second all empty
#     mock_get.side_effect = [
#         MagicMock(json=lambda: {"email": None, "name": "Ghost", "login": "ghost"}),
#         MagicMock(json=lambda: []),
#     ]

#     # ACT
#     response = api_client.get(url, {"code": "valid_code", "state": "test_state"})

#     print(response["Location"])
#     print(response["Location"], flush=True)
#     # ASSERT
#     assert response.status_code == 302
#     assert "error=no_email" in response["Location"]


# @patch("backend.views.requests.get")
# @patch("backend.views.requests.post")
# def test_new_user_created_and_redirected_success(
#     mock_post, mock_get, api_client, settings
# ):
#     """
#     Should create a new user and return token.
#     """
#     # ARRANGE
#     settings.FRONTEND_URL = "http://localhost:3000"
#     settings.GITHUB_CLIENT_ID = "fake_client_id"
#     settings.GITHUB_CLIENT_SECRET = "fake_secret"
#     settings.GITHUB_CALLBACK_URL = "http://localhost:8000/api/auth/github/callback/"
#     url = reverse("github_callback")

#     session = api_client.session
#     session["github_oauth_state"] = "test_state"
#     session.save()

#     mock_post.return_value = MagicMock(json=lambda: {"access_token": "fake_token"})
#     mock_get.return_value = MagicMock(
#         json=lambda: {
#             "email": "newuser@github.com",
#             "name": "Jane Doe",
#             "login": "janedoe",
#         }
#     )

#     # ACT
#     response = api_client.get(url, {"code": "valid_code", "state": "test_state"})

#     # ASSERT
#     assert response.status_code == 302
#     assert "/auth/callback" in response["Location"]
#     assert User.objects.filter(email="newuser@github.com").exists()


# @patch("backend.views.requests.get")
# @patch("backend.views.requests.post")
# def test_user_created_with_correct_name_success(
#     mock_post, mock_get, api_client, settings, user
# ):
#     """
#     Should properly retrieve first and last name.
#     """
#     # ARRANGE
#     settings.FRONTEND_URL = "http://localhost:3000"
#     settings.GITHUB_CLIENT_ID = "fake_client_id"
#     settings.GITHUB_CLIENT_SECRET = "fake_secret"
#     settings.GITHUB_CALLBACK_URL = "http://localhost:8000/api/auth/github/callback/"
#     url = reverse("github_callback")

#     mock_post.return_value = MagicMock(json=lambda: {"access_token": "fake_token"})
#     mock_get.return_value = MagicMock(
#         json=lambda: {
#             "email": "john@example.com",
#             "name": "John Doe",
#             "login": "JD",
#         }
#     )

#     # ACT
#     api_client.get(url, {"code": "valid_code"})

#     # ASSERT
#     assert user.first_name == "John"
#     assert user.last_name == "Doe"


# @patch("backend.views.requests.get")
# @patch("backend.views.requests.post")
# def test_email_fetched_from_emails_endpoint_success(
#     mock_post, mock_get, api_client, settings
# ):
#     """
#     Should retrieve email from verified emails.
#     """
#     # ARRANGE
#     settings.FRONTEND_URL = "http://localhost:3000"
#     settings.GITHUB_CLIENT_ID = "fake_client_id"
#     settings.GITHUB_CLIENT_SECRET = "fake_secret"
#     settings.GITHUB_CALLBACK_URL = "http://localhost:8000/api/auth/github/callback/"
#     url = reverse("github_callback")

#     session = api_client.session
#     session["github_oauth_state"] = "test_state"
#     session.save()

#     mock_post.return_value = MagicMock(json=lambda: {"access_token": "fake_token"})
#     mock_get.side_effect = [
#         MagicMock(
#             json=lambda: {"email": None, "name": "Private User", "login": "privateuser"}
#         ),
#         MagicMock(
#             json=lambda: [
#                 {"email": "private@github.com", "primary": True, "verified": True},
#             ]
#         ),
#     ]

#     # ACT
#     response = api_client.get(url, {"code": "valid_code", "state": "test_state"})

#     # ASSERT
#     assert response.status_code == 302
#     assert User.objects.filter(email="private@github.com").exists()


@patch("backend.views.RefreshToken")
def test_logout_view_blacklists_refresh_token_success(
    mock_refresh_token_class, authenticated_client
):
    """
    Should blacklist refresh token when cookie is present
    """
    # ARRANGE
    url = reverse("logout")
    mock_refresh_token_class.return_value = MagicMock()
    authenticated_client.cookies["refresh_token"] = "new_refresh_token"

    # ACT
    response = authenticated_client.post(url)

    # ASSERT
    assert response.status_code == 200
    assert response.data["detail"] == "Déconnecté."

    mock_refresh_token_class.assert_called_once_with("new_refresh_token")

    cookies = response.cookies
    assert "refresh_token" in cookies


@patch("backend.views.logger.warning")
@patch("backend.views.RefreshToken")
def test_logout_view_logs_warning_if_blacklist_fails(
    mock_refresh_token_class, mock_logger_warning, authenticated_client
):
    """
    Should logout if refresh token blacklist fails
    """
    # ARRANGE
    url = reverse("logout")
    mock_refresh_token_class.side_effect = Exception("blacklist failed")
    authenticated_client.cookies["refresh_token"] = "new_refresh_token"

    # ACT
    response = authenticated_client.post(url)

    # ASSERT
    assert response.status_code == 200
    assert response.data["detail"] == "Déconnecté."

    mock_refresh_token_class.assert_called_once_with("new_refresh_token")
    mock_logger_warning.assert_called_once()

    cookies = response.cookies
    assert "refresh_token" in cookies
