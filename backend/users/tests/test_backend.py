from django.test import TestCase
from users.backend import EmailBackend


class EmailBackendTests(TestCase):
    def test_authenticate_no_email(self):
        """
        Test authenticate returns None when no email is provided.
        """
        backend = EmailBackend()
        user = backend.authenticate(request=None, username=None, password="test")
        self.assertIsNone(user)
