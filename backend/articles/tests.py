from django.test import TestCase
from django.urls import reverse


class ArticlesViewsTest(TestCase):
    def test_index_view_success(self):
        """
            Simple test to assert the article index
                will be remove later.
        """
        url = reverse('articles-index')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello, world. You're at the articles index.")