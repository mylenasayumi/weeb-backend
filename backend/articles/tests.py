from django.test import TestCase
from django.urls import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User
import json
from .models import Article


class ArticleViewTests(TestCase):
    """
    Unit tests for the ArticleViewSet.
    """

    def setUp(self):
        """
        Create example of articles.
        """
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_login(self.user)
        
        self.article1 = Article.objects.create(
            title="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            description="Quisque vitae felis vestibulum, auctor erat vitae, feugiat purus..",
            image="https://en.wikipedia.org/wiki/Lorem_ipsum#/media/File:Lorem_ipsum_design.svg",
            user=self.user
        )
        self.article2 = Article.objects.create(
            title="Pellentesque blandit lacus eu porttitor euismod.",
            description="Etiam scelerisque ipsum sit amet consequat ornare.",
            image="https://en.wikipedia.org/wiki/Lorem_ipsum#/media/File:Lorem_ipsum_design.svg",
            user=self.user
        )
        self.list_url = reverse('article-list')
        self.detail_url = lambda pk: reverse('article-detail', args=[pk])

    ############ CREATE ############
    def test_create_article_success(self):
        """
        Should create a new article when valid data is provided.
        """
        data = {
            "title": "Suspendisse imperdiet est id nunc venenatis, eu dictum dui ultricies.",
            "description": "Maecenas eu justo efficitur tortor vehicula semper.",
            "image": "https://en.wikipedia.org/wiki/Lorem_ipsum#/media/File:Lorem_ipsum_design.svg",
            "user": self.user.id
        }
        response = self.client.post(
            self.list_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Article.objects.count(), 3)
        self.assertEqual(Article.objects.last().title, data["title"])

        # Check if response contains the expected fields
        self.assertIn("id", response.json())
        self.assertIn("title", response.json())
        self.assertEqual(response.json()["user"], self.user.id)

    def test_create_article_invalid_title(self):
        """
        Should reject a title with fewer than 5 characters.
        """
        data = {"title": "API", "description": "Test", "image": "", "user": self.user.id}
        response = self.client.post(
            self.list_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json())

    def test_create_article_empty_description(self):
        """
        Should reject an empty description.
        """
        data = {"title": "Valid Article", "description": "   ", "image": "", "user": self.user.id}
        response = self.client.post(
            self.list_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("description", response.json())

    ############ LIST & RETRIEVE ############
    def test_list_articles_with_pagination(self):
        """
        Should return a paginated list of articles.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertIn("total_count", data)
        self.assertTrue(len(data["results"]) >= 1)

    def test_retrieve_article(self):
        """
        Should return the details of a specific article.
        """
        response = self.client.get(self.detail_url(self.article1.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], self.article1.title)
        self.assertEqual(response.json()["user"], self.user.id)

    ############ SEARCH & ORDERING ############
    def test_search_article_by_title(self):
        """
        Should filter articles by title using the search parameter.
        """
        response = self.client.get(f"{self.list_url}?search=Lorem")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(any("lorem" in a["title"].lower() for a in data["results"]))

    def test_ordering_articles_by_title(self):
        """
        Should order articles alphabetically by title.
        """
        response = self.client.get(f"{self.list_url}?ordering=title")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        titles = [a["title"] for a in data["results"]]
        self.assertEqual(titles, sorted(titles))

    ############ UPDATE ############
    def test_update_article(self):
        """
        Should update an existing article.
        """
        data = {
            "title": "New Title",
            "description": "Updated description",
            "image": self.article1.image,
            "user": self.user.id
        }
        response = self.client.put(
            self.detail_url(self.article1.pk),
            data=json.dumps(data, cls=DjangoJSONEncoder),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.article1.refresh_from_db()
        self.assertEqual(self.article1.title, "New Title")

    ############ DELETE ############
    def test_delete_article(self):
        """
        Should delete an existing article.
        """
        response = self.client.delete(self.detail_url(self.article1.pk))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Article.objects.filter(pk=self.article1.pk).exists())