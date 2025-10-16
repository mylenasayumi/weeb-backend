from django.test import TestCase


class ArticlesViewsTest(TestCase):
    def test_index_view_success(self):
        """
        Simple test to assert the article index
            will be remove later.
        """
        response = self.client.get("/articles/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello, world. You're at the articles index.")
