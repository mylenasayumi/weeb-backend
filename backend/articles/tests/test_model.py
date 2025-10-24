from articles.models import Article
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UsersModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="john@example.com",
            password="pass12345",
            first_name="John",
            last_name="Doe",
        )

        self.article = Article.objects.create(
            title="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            description="Quisque vitae felis vestibulum, auctor erat vitae, feugiat purus..",
            image="https://en.wikipedia.org/wiki/Lorem_ipsum#/media/File:Lorem_ipsum_design.svg",
            user=self.user,
        )

    def test_get_str_success(self):
        """
        Test __str__ method returns correct string.
        """
        expected_output = (
            "title: Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        )

        self.assertIn(self.article.__str__(), expected_output)
