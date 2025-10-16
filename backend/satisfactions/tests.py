from django.test import TestCase

class SatisfactionsViewsTest(TestCase):
    def test_index_view_success(self):
        """
            Simple test to assert the satisfaction index
                will be remove later.
        """
        response = self.client.get('/satisfactions/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello, world. You're at the satisfactions index.")