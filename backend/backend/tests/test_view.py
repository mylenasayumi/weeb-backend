from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.urls import reverse

User = get_user_model()

# Indicate to pytest that it needs access to db
pytestmark = pytest.mark.django_db


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


def test_no_code_redirects_failure(api_client, settings):
    """
    Should return no_code if no code il url.
    """
    # ARRANGE
    settings.FRONTEND_URL = "http://localhost:3000"
    url = reverse("github_callback")

    # ACT
    response = api_client.get(url)

    # ASSERT
    assert response.status_code == 302
    assert "error=no_code" in response["Location"]


@patch("backend.views.requests.post")
def test_invalid_github_token_redirects_failure(mock_post, api_client, settings):
    """
    Should return an error if github return no token.
    """
    # ARRAGE
    settings.FRONTEND_URL = "http://localhost:3000"
    settings.GITHUB_CLIENT_ID = "fake_client_id"
    settings.GITHUB_CLIENT_SECRET = "fake_secret"
    settings.GITHUB_CALLBACK_URL = "http://localhost:8000/api/auth/github/callback/"
    url = reverse("github_callback")

    mock_post.return_value = MagicMock(json=lambda: {"error": "bad_verification_code"})

    # ACT
    response = api_client.get(url, {"code": "invalid_code"})

    # ASSERT
    assert response.status_code == 302
    assert "error=token_failed" in response["Location"]


@patch("backend.views.requests.get")
@patch("backend.views.requests.post")
def test_no_email_redirects_failure(mock_post, mock_get, api_client, settings):
    """
    Should return an error if no email is found.
    """
    # ARRANGE
    settings.FRONTEND_URL = "http://localhost:3000"
    settings.GITHUB_CLIENT_ID = "fake_client_id"
    settings.GITHUB_CLIENT_SECRET = "fake_secret"
    settings.GITHUB_CALLBACK_URL = "http://localhost:8000/api/auth/github/callback/"
    url = reverse("github_callback")

    mock_post.return_value = MagicMock(json=lambda: {"access_token": "fake_token"})

    # First email empty second all empty
    mock_get.side_effect = [
        MagicMock(json=lambda: {"email": None, "name": "Ghost", "login": "ghost"}),
        MagicMock(json=lambda: []),
    ]

    # ACT
    response = api_client.get(url, {"code": "valid_code"})

    # ASSERT
    assert response.status_code == 302
    assert "error=no_email" in response["Location"]


@patch("backend.views.requests.get")
@patch("backend.views.requests.post")
def test_new_user_created_and_redirected_success(
    mock_post, mock_get, api_client, settings
):
    """
    Should create a new user and return token.
    """
    # ARRANGE
    settings.FRONTEND_URL = "http://localhost:3000"
    settings.GITHUB_CLIENT_ID = "fake_client_id"
    settings.GITHUB_CLIENT_SECRET = "fake_secret"
    settings.GITHUB_CALLBACK_URL = "http://localhost:8000/api/auth/github/callback/"
    url = reverse("github_callback")

    mock_post.return_value = MagicMock(json=lambda: {"access_token": "fake_token"})
    mock_get.return_value = MagicMock(
        json=lambda: {
            "email": "newuser@github.com",
            "name": "Jane Doe",
            "login": "janedoe",
        }
    )

    # ACT
    response = api_client.get(url, {"code": "valid_code"})

    # ASSERT
    assert response.status_code == 302
    assert "/auth/callback" in response["Location"]
    assert "refresh=" in response["Location"]
    assert User.objects.filter(email="newuser@github.com").exists()


@patch("backend.views.requests.get")
@patch("backend.views.requests.post")
def test_user_created_with_correct_name_success(
    mock_post, mock_get, api_client, settings, user
):
    """
    Should properly retrieve first and last name.
    """
    # ARRANGE
    settings.FRONTEND_URL = "http://localhost:3000"
    settings.GITHUB_CLIENT_ID = "fake_client_id"
    settings.GITHUB_CLIENT_SECRET = "fake_secret"
    settings.GITHUB_CALLBACK_URL = "http://localhost:8000/api/auth/github/callback/"
    url = reverse("github_callback")

    mock_post.return_value = MagicMock(json=lambda: {"access_token": "fake_token"})
    mock_get.return_value = MagicMock(
        json=lambda: {
            "email": "john@example.com",
            "name": "John Doe",
            "login": "JD",
        }
    )

    # ACT
    api_client.get(url, {"code": "valid_code"})

    # ASSERT
    assert user.first_name == "John"
    assert user.last_name == "Doe"


@patch("backend.views.requests.get")
@patch("backend.views.requests.post")
def test_email_fetched_from_emails_endpoint_success(
    mock_post, mock_get, api_client, settings
):
    """
    Should retrieve email from verified emails.
    """
    # ARRANGE
    settings.FRONTEND_URL = "http://localhost:3000"
    settings.GITHUB_CLIENT_ID = "fake_client_id"
    settings.GITHUB_CLIENT_SECRET = "fake_secret"
    settings.GITHUB_CALLBACK_URL = "http://localhost:8000/api/auth/github/callback/"
    url = reverse("github_callback")

    mock_post.return_value = MagicMock(json=lambda: {"access_token": "fake_token"})
    mock_get.side_effect = [
        MagicMock(
            json=lambda: {"email": None, "name": "Private User", "login": "privateuser"}
        ),
        MagicMock(
            json=lambda: [
                {"email": "private@github.com", "primary": True, "verified": True},
            ]
        ),
    ]

    # ACT
    response = api_client.get(url, {"code": "valid_code"})

    # ASSERT
    assert response.status_code == 302
    assert User.objects.filter(email="private@github.com").exists()
