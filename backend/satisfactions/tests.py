from django.test import TestCase
from django.urls import reverse

class SatisfactionsViewsTest(TestCase):
    def test_index_view_success(self):
        """
            Simple test to assert the satisfaction index
                will be remove later.
        """
        url = reverse('satisfaction-index')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)