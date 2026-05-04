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


def test_github_login_unauthorized_origin_failure(api_client, settings):
    """
    Should return 403 if Referer origin is not in CORS_ALLOWED_ORIGINS (prod mode).
    """
    # ARRANGE
    settings.CORS_ALLOW_ALL_ORIGINS = False
    settings.CORS_ALLOWED_ORIGINS = ["http://allowed-frontend.com"]
    settings.GITHUB_CLIENT_ID = "fake_client_id"
    settings.GITHUB_CALLBACK_URL = "http://localhost:8000/api/auth/github/callback/"
    url = reverse("github_login")

    # ACT
    response = api_client.get(url, HTTP_REFERER="http://evil-frontend.com/some/path")

    # ASSERT
    assert response.status_code == 403
    assert response.json()["error"] == "Unauthorized origin"


def test_no_code_redirects_failure(api_client, settings):
    """
    Should return no_code if no code il url.
    """
    # ARRANGE
    settings.FRONTEND_URL = "http://localhost:3000"
    url = reverse("exchange_code")

    session = api_client.session
    session["github_oauth_state"] = "test_state"
    session.save()

    # ACT
    response = api_client.post(url, {"state": "test_state"})

    # ASSERT
    assert response.status_code == 400
    assert response.json()["error"] == "Missing code"


def test_exchange_oauth_code_invalid_or_expired_code_failure(api_client):
    """
    Should return 400 if code is not found in cache (invalid or expired).
    """
    # ARRANGE
    url = reverse("exchange_code")
    payload = {"code": "nonexistent_code"}

    # ACT
    with patch("django.core.cache.cache.get", return_value=None):
        response = api_client.post(url, payload, format="json")

    # ASSERT
    assert response.status_code == 400
    assert response.json()["error"] == "Invalid or expired code"


def test_exchange_oauth_code_deletes_cache_after_use(api_client):
    """
    Should delete the cache entry after a successful exchange (one-time use).
    """
    # ARRANGE
    url = reverse("exchange_code")
    payload = {"code": "valid_code"}
    fake_tokens = {"access": "fake_access_token", "refresh": "fake_refresh_token"}

    # ACT
    with patch(
        "django.core.cache.cache.get", return_value=fake_tokens
    ) as mock_get, patch("django.core.cache.cache.delete") as mock_delete:
        api_client.post(url, payload, format="json")

    # ASSERT
    mock_get.assert_called_once_with("oauth_temp:valid_code")
    mock_delete.assert_called_once_with("oauth_temp:valid_code")


def test_github_callback_missing_frontend_url_failure(api_client, settings):
    """
    Should return 403 if frontend_url is missing from session.
    """
    # ARRANGE
    settings.CORS_ALLOWED_ORIGINS = ["http://allowed-frontend.com"]
    url = reverse("github_callback")

    # ACT
    response = api_client.get(url)

    # ASSERT
    assert response.status_code == 403
    assert response.json()["error"] == "Unauthorized origin"


def test_github_callback_unauthorized_frontend_url_failure(api_client, settings):
    """
    Should return 403 if frontend_url is not in CORS_ALLOWED_ORIGINS.
    """
    # ARRANGE
    settings.CORS_ALLOWED_ORIGINS = ["http://allowed-frontend.com"]
    url = reverse("github_callback")
    session = api_client.session
    session["github_oauth_frontend"] = "http://evil-frontend.com"
    session.save()

    # ACT
    response = api_client.get(url)

    # ASSERT
    assert response.status_code == 403
    assert response.json()["error"] == "Unauthorized origin"


def test_github_callback_invalid_state_failure(api_client, settings):
    """
    Should redirect to /login?error=invalid_state if state does not match.
    """
    # ARRANGE
    settings.CORS_ALLOWED_ORIGINS = ["http://allowed-frontend.com"]
    url = reverse("github_callback")
    session = api_client.session
    session["github_oauth_frontend"] = "http://allowed-frontend.com"
    session["github_oauth_state"] = "correct_state"
    session.save()

    # ACT
    response = api_client.get(url, {"code": "somecode", "state": "wrong_state"})

    # ASSERT
    assert response.status_code == 302
    assert "error=invalid_state" in response["Location"]


def test_github_callback_missing_code_failure(api_client, settings):
    """
    Should redirect to /login?error=no_code if code is missing.
    """
    # ARRANGE
    settings.CORS_ALLOWED_ORIGINS = ["http://allowed-frontend.com"]
    url = reverse("github_callback")
    session = api_client.session
    session["github_oauth_frontend"] = "http://allowed-frontend.com"
    session["github_oauth_state"] = "correct_state"
    session.save()

    # ACT
    response = api_client.get(url, {"state": "correct_state"})

    # ASSERT
    assert response.status_code == 302
    assert "error=no_code" in response["Location"]


def test_github_callback_token_exchange_failed_failure(api_client, settings):
    """
    Should redirect to /login?error=token_failed if GitHub does not return an access_token.
    """
    # ARRANGE
    settings.CORS_ALLOWED_ORIGINS = ["http://allowed-frontend.com"]
    settings.GITHUB_CLIENT_ID = "fake_client_id"
    settings.GITHUB_CLIENT_SECRET = "fake_secret"
    settings.GITHUB_CALLBACK_URL = "http://localhost:8000/api/auth/github/callback/"
    url = reverse("github_callback")
    session = api_client.session
    session["github_oauth_frontend"] = "http://allowed-frontend.com"
    session["github_oauth_state"] = "correct_state"
    session.save()

    mock_token_response = MagicMock()
    mock_token_response.json.return_value = {}

    # ACT
    with patch("requests.post", return_value=mock_token_response):
        response = api_client.get(url, {"code": "somecode", "state": "correct_state"})

    # ASSERT
    assert response.status_code == 302
    assert "error=token_failed" in response["Location"]


def test_github_callback_no_email_anywhere_failure(api_client, settings):
    """
    Should redirect to /login?error=no_email if no email found on profile or /user/emails.
    """
    # ARRANGE
    settings.CORS_ALLOWED_ORIGINS = ["http://allowed-frontend.com"]
    settings.GITHUB_CLIENT_ID = "fake_client_id"
    settings.GITHUB_CLIENT_SECRET = "fake_secret"
    settings.GITHUB_CALLBACK_URL = "http://localhost:8000/api/auth/github/callback/"
    url = reverse("github_callback")
    session = api_client.session
    session["github_oauth_frontend"] = "http://allowed-frontend.com"
    session["github_oauth_state"] = "correct_state"
    session.save()

    mock_token_response = MagicMock()
    mock_token_response.json.return_value = {"access_token": "fake_github_token"}

    mock_user_response = MagicMock()
    mock_user_response.json.return_value = {
        "email": None,
        "name": "John Doe",
        "login": "johndoe",
    }

    mock_emails_response = MagicMock()
    mock_emails_response.json.return_value = []

    # ACT
    with patch("requests.post", return_value=mock_token_response), patch(
        "requests.get", side_effect=[mock_user_response, mock_emails_response]
    ):
        response = api_client.get(url, {"code": "somecode", "state": "correct_state"})

    # ASSERT
    assert response.status_code == 302
    assert "error=no_email" in response["Location"]


def test_github_callback_success_with_email_on_profile(api_client, settings):
    """
    Should create user and redirect to /auth/callback?code=... when email is on GitHub profile.
    """
    # ARRANGE
    settings.CORS_ALLOWED_ORIGINS = ["http://allowed-frontend.com"]
    settings.GITHUB_CLIENT_ID = "fake_client_id"
    settings.GITHUB_CLIENT_SECRET = "fake_secret"
    settings.GITHUB_CALLBACK_URL = "http://localhost:8000/api/auth/github/callback/"
    url = reverse("github_callback")
    session = api_client.session
    session["github_oauth_frontend"] = "http://allowed-frontend.com"
    session["github_oauth_state"] = "correct_state"
    session.save()

    mock_token_response = MagicMock()
    mock_token_response.json.return_value = {"access_token": "fake_github_token"}

    mock_user_response = MagicMock()
    mock_user_response.json.return_value = {
        "email": "john@example.com",
        "name": "John Doe",
        "login": "johndoe",
    }

    # ACT
    with patch("requests.post", return_value=mock_token_response), patch(
        "requests.get", return_value=mock_user_response
    ), patch("django.core.cache.cache.set") as mock_cache_set:
        response = api_client.get(url, {"code": "somecode", "state": "correct_state"})

    # ASSERT
    assert response.status_code == 302
    assert "/auth/callback?code=" in response["Location"]
    mock_cache_set.assert_called_once()
    assert User.objects.filter(email="john@example.com").exists()


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
