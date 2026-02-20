from articles.models import Article
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class ArticleViewTests(APITestCase):
    """
    Unit tests for the ArticleViewSet.
    """

    def setUp(self):
        """
        Create example of articles.
        """
        self.user = User.objects.create_user(
            email="john@example.com",
            password="pass12345",
            first_name="John",
            last_name="Doe",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.article1 = Article.objects.create(
            title="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            description="Quisque vitae felis vestibulum, auctor erat vitae, feugiat purus..",
            image="https://en.wikipedia.org/wiki/Lorem_ipsum#/media/File:Lorem_ipsum_design.svg",
            user=self.user,
        )
        self.article2 = Article.objects.create(
            title="Pellentesque blandit lacus eu porttitor euismod.",
            description="Etiam scelerisque ipsum sit amet consequat ornare.",
            image="https://en.wikipedia.org/wiki/Lorem_ipsum#/media/File:Lorem_ipsum_design.svg",
            user=self.user,
        )
        self.list_url = reverse("articles-list")

        self.detail_url = lambda pk: reverse("articles-detail", args=[pk])

    ############ CREATE ############
    def test_create_article_success(self):
        """
        Should create a new article when valid data is provided.
        """
        data = {
            "title": "Suspendisse imperdiet est id nunc venenatis, eu dictum dui ultricies.",
            "description": "Maecenas eu justo efficitur tortor vehicula semper.",
            "image": "https://en.wikipedia.org/wiki/Lorem_ipsum#/media/File:Lorem_ipsum_design.svg",
        }
        response = self.client.post(self.list_url, data=data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Article.objects.count(), 3)
        self.assertEqual(Article.objects.last().title, data["title"])

        # Check if response contains the expected fields
        self.assertIn("id", response.json())
        self.assertIn("title", response.json())

    def test_create_article_invalid_title_failure(self):
        """
        Should reject a title with fewer than 5 characters.
        """
        data = {
            "title": "API",
            "description": "Test",
            "image": "",
            "user": self.user.id,
        }
        response = self.client.post(self.list_url, data=data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json())

    def test_create_article_empty_description_failure(self):
        """
        Should reject an empty description with custom validation error.
        """
        data = {"title": "Valid Article", "description": "   ", "image": ""}
        expected_output = "Description cannot be empty."
        response = self.client.post(self.list_url, data=data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["description"][0], expected_output)

    ############ LIST & RETRIEVE ############
    def test_list_articles_with_pagination_success(self):
        """
        Should return a paginated list of articles.
        """
        response = self.client.get(self.list_url)
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("results", data)
        self.assertIn("count", data)
        self.assertTrue(len(data["results"]) >= 1)

    def test_retrieve_article_success(self):
        """
        Should return the details of a specific article.
        """
        response = self.client.get(self.detail_url(self.article1.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], self.article1.title)
        self.assertEqual(response.json()["user"], self.user.id)

    ############ SEARCH & ORDERING ############
    def test_search_article_by_title_success(self):
        """
        Should filter articles by title using the search parameter.
        """
        response = self.client.get(f"{self.list_url}?search=Lorem")
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(any("lorem" in a["title"].lower() for a in data["results"]))

    def test_ordering_articles_by_title_success(self):
        """
        Should order articles alphabetically by title.
        """
        response = self.client.get(f"{self.list_url}?ordering=title")
        data = response.json()

        self.assertEqual(response.status_code, 200)
        titles = [a["title"] for a in data["results"]]
        self.assertEqual(titles, sorted(titles))

    ############ UPDATE ############
    def test_update_article_success(self):
        """
        Should update an existing article.
        """
        data = {
            "title": "New Title",
            "description": "Updated description",
            "image": self.article1.image,
            "user": self.user.id,
        }
        response = self.client.put(
            self.detail_url(self.article1.pk), data=data, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.article1.refresh_from_db()
        self.assertEqual(self.article1.title, "New Title")

    ############ PARTIAL UPDATE ############
    def test_partial_update_article_success(self):
        """
        Should partial uppdate an existing article.
        """
        data = {
            "description": "Updated description Partial Update",
        }
        response = self.client.patch(
            self.detail_url(self.article1.pk), data=data, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.article1.refresh_from_db()
        self.assertNotEqual(self.article1.title, data["description"])

    ############ DELETE ############
    def test_delete_article_success(self):
        """
        Should delete an existing article.
        """
        response = self.client.delete(self.detail_url(self.article1.pk))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Article.objects.filter(pk=self.article1.pk).exists())

    def test_update_article_not_owner_failure(self):
        """
        Should prevent a user from updating an article they do not own.
        """
        data = {
            "title": "Unauthorized Update Attempt",
            "description": "This should fail.",
        }

        other_user = User.objects.create_user(
            email="other@example.com",
            password="pass12345",
            first_name="Other",
            last_name="User",
        )

        self.client.force_authenticate(user=other_user)

        response = self.client.put(
            self.detail_url(self.article1.pk), data=data, format="json"
        )

        self.assertEqual(response.status_code, 403)
        self.assertIn(
            "You do not have permission to perform this action.",
            str(response.data["detail"]),
        )
