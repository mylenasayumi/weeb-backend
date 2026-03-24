import pytest
from articles.models import Article
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()

# Indicate to pytest that it needs access to db
pytestmark = pytest.mark.django_db


############ CREATE ############
def test_create_article_success(authenticated_client, article, article2):
    """
    Should create a new article when valid data is provided.
    We add article and article2 to force creation.
    """
    # ARRANGE
    data = {
        "title": "Suspendisse imperdiet est id nunc venenatis, eu dictum dui ultricies.",
        "description": "Maecenas eu justo efficitur tortor vehicula semper.",
        "image": "https://en.wikipedia.org/wiki/Lorem_ipsum#/media/File:Lorem_ipsum_design.svg",
    }
    list_url = reverse("articles-list")

    # ACT
    response = authenticated_client.post(list_url, data=data, format="json")

    # ASSERT
    assert response.status_code == 201
    assert Article.objects.count() == 3
    assert Article.objects.last().title == data["title"]
    assert "id" in response.json()
    assert "title" in response.json()


def test_create_article_invalid_title_failure(authenticated_client):
    """
    Should reject a title with fewer than 5 characters.
    """
    # ARRANGE
    data = {
        "title": "API",
        "description": "Test",
        "image": "",
    }
    list_url = reverse("articles-list")

    # ACT
    response = authenticated_client.post(list_url, data=data, format="json")

    # ASSERT
    assert response.status_code == 400
    assert "title" in response.json()


def test_create_article_empty_description_failure(authenticated_client):
    """
    Should reject an empty description with custom validation error.
    """
    data = {"title": "Valid Article", "description": "   ", "image": ""}
    expected_output = "Description cannot be empty."
    list_url = reverse("articles-list")

    response = authenticated_client.post(list_url, data=data, format="json")

    # ASSERT
    assert response.status_code == 400
    assert response.json()["description"][0] in expected_output


def test_set_views_on_create_failure(authenticated_client):
    """
    Should ignore any attempt to set views on article creation.
    """
    data = {
        "title": "Article with Views",
        "description": "This article tries to set views on creation.",
        "image": "",
        "views": 100,
    }
    list_url = reverse("articles-list")

    response = authenticated_client.post(list_url, data=data, format="json")

    assert response.status_code == 201
    assert response.json()["views"] == 0


############ LIST & RETRIEVE ############
def test_list_articles_with_pagination_success(authenticated_client, article):
    """
    Should return a paginated list of articles.
    """
    list_url = reverse("articles-list")

    response = authenticated_client.get(list_url)
    data = response.json()

    assert response.status_code == 200
    assert "results" in data
    assert "count" in data
    assert len(data["results"]) >= 1


def test_retrieve_article_success(authenticated_client, article):
    """
    Should return the details of a specific article and increment views.
    """
    detail_url = reverse("articles-detail", args=[article.pk])

    initial_views = article.views

    response = authenticated_client.get(detail_url)

    article.refresh_from_db()

    assert response.status_code == 200
    assert response.json()["title"] == article.title
    assert response.json()["user"] == article.user.id
    assert response.json()["views"] == initial_views + 1


def test_article_views_increment_multiple_times_success(authenticated_client, article):
    """
    Should increment the views count each time the article is retrieved.
    """
    detail_url = reverse("articles-detail", args=[article.pk])

    initial_views = article.views

    # Retrieve the article 3 times
    for _ in range(3):
        response = authenticated_client.get(detail_url)
        assert response.status_code == 200

    article.refresh_from_db()

    assert article.views == initial_views + 3


############ SEARCH & ORDERING ############
def test_search_article_by_title_success(authenticated_client, article, article2):
    """
    Should filter articles by title using the search parameter.
    """
    list_url = reverse("articles-list")

    response = authenticated_client.get(f"{list_url}?search=Lorem")
    data = response.json()

    assert response.status_code == 200
    assert any("lorem" in a["title"].lower() for a in data["results"])


def test_ordering_articles_by_title_success(authenticated_client):
    """
    Should order articles alphabetically by title.
    """
    list_url = reverse("articles-list")

    response = authenticated_client.get(f"{list_url}?ordering=title")
    data = response.json()

    assert response.status_code == 200
    titles = [a["title"] for a in data["results"]]
    assert titles == sorted(titles)


############ UPDATE ############
def test_update_article_success(authenticated_client, article, user):
    """
    Should update an existing article.
    """
    # ARRANGE
    detail_url = reverse("articles-detail", args=[article.pk])
    data = {
        "title": "New Title",
        "description": "Updated description",
        "image": article.image,
        "user": user.id,
    }

    # ACT
    response = authenticated_client.put(detail_url, data=data, format="json")
    # ASSERT
    assert response.status_code == 200
    article.refresh_from_db()
    assert article.title == "New Title"


############ PARTIAL UPDATE ############
def test_partial_update_article_success(authenticated_client, article):
    """
    Should partial uppdate an existing article.
    """
    data = {
        "description": "Updated description Partial Update",
    }
    detail_url = reverse("articles-detail", args=[article.pk])

    response = authenticated_client.patch(detail_url, data=data, format="json")

    assert response.status_code == 200
    article.refresh_from_db()
    assert article.title != data["description"]


############ DELETE ############
def test_delete_article_success(authenticated_client, article):
    """
    Should delete an existing article.
    """
    detail_url = reverse("articles-detail", args=[article.pk])

    response = authenticated_client.delete(detail_url)

    assert response.status_code == 204
    assert Article.objects.filter(pk=article.pk).exists() == False


def test_update_article_not_owner_failure(article):
    """
    Should prevent a user from updating an article they do not own.
    """
    # ARRANGE
    other_user = User.objects.create_user(
        email="other@example.com",
        password="pass12345",
        first_name="Other",
        last_name="User",
    )
    other_client = APIClient()
    other_client.force_authenticate(user=other_user)
    detail_url = reverse("articles-detail", args=[article.pk])
    data = {
        "title": "Unauthorized Update Attempt",
        "description": "This should fail.",
    }

    # ACT
    response = other_client.put(detail_url, data=data, format="json")

    # ASSERT
    assert response.status_code == 403
    assert "You do not have permission to perform this action." in str(
        response.data["detail"]
    )
