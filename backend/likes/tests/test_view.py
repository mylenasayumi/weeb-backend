import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.urls import reverse
from likes.models import Like

User = get_user_model()

# Indicate to pytest that it needs access to db
pytestmark = pytest.mark.django_db


def test_list_unauthenticated_failure(api_client):
    """
    Should not retrieve likes if user not authenticated.
    """
    # ARRANGE
    url = reverse("likes-list")

    # ACT
    response = api_client.get(url)

    # ASSERT
    assert response.status_code == 401


def test_list_empty(authenticated_client):
    """
    Should return empty list if no like.
    """
    # ARRANGE
    url = reverse("likes-list")

    # ACT
    response = authenticated_client.get(url)

    # ASSERT
    assert response.status_code == 200
    assert response.data == []


def test_list_returns_only_user_likes(
    authenticated_client, user, user2, article, article2
):
    """
    Should returns only  list of articles liked by the user.
    """
    # ARRANGE
    Like.objects.create(user=user, article=article)
    Like.objects.create(user=user2, article=article2)
    url = reverse("likes-list")

    # ACT
    response = authenticated_client.get(url)

    # ARRANGE
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["article"]["id"] == article.id


def test_toggle_unauthenticated_failure(api_client, article):
    """
    Should return 401 for unauthentified user.
    """
    # ARRANGE
    url = reverse("likes-toggle", kwargs={"pk": article.id})

    # ACT
    response = api_client.post(url)

    # ASSERT
    assert response.status_code == 401


def test_toggle_like_article_success(authenticated_client, article):
    """
    Should like an artile and see true.
    """
    # ARRANGE
    url = reverse("likes-toggle", kwargs={"pk": article.id})

    # ACT
    response = authenticated_client.post(url)

    # ASSERT
    assert response.status_code == 201
    assert response.data["liked"] is True
    assert response.data["message"] == "Article liked"
    assert Like.objects.count() == 1


def test_toggle_unlike_article_success(authenticated_client, user, article, like):
    """
    Should unlike a like if it is liked.
    """
    # ARANGE
    url = reverse("likes-toggle", kwargs={"pk": article.id})

    # ACT
    response = authenticated_client.post(url)

    # ASSERT
    assert response.status_code == 200
    assert response.data["liked"] is False
    assert response.data["message"] == "Like removed"
    assert Like.objects.count() == 0


def test_toggle_article_do_not_exist_failure(authenticated_client):
    """
    Should returns 404 if article does not exist.
    """
    # ARRANGE
    url = reverse("likes-toggle", kwargs={"pk": 99999})

    # ACT
    response = authenticated_client.post(url)

    # ASSERT
    assert response.status_code == 404


def test_toggle_like_success(authenticated_client, article):
    """
    Should like multiple times
    """
    url = reverse("likes-toggle", kwargs={"pk": article.id})

    # Like
    response = authenticated_client.post(url)
    assert response.status_code == 201
    assert Like.objects.count() == 1

    # Unlike
    response = authenticated_client.post(url)
    assert response.status_code == 200
    assert Like.objects.count() == 0

    # Like again
    response = authenticated_client.post(url)
    assert response.status_code == 201
    assert Like.objects.count() == 1


def test_two_users_toggle_same_article_success(api_client, user, user2, article):
    """
    Should two users like same article.
    """
    # ARRANGE
    url = reverse("likes-toggle", kwargs={"pk": article.id})

    # ACT
    api_client.force_authenticate(user=user)
    api_client.post(url)

    api_client.force_authenticate(user=user2)
    api_client.post(url)

    # ASSERT
    assert Like.objects.count() == 2

    # unlike
    api_client.post(url)
    # ASSERT
    assert Like.objects.count() == 1
    assert Like.objects.filter(user=user).exists()
