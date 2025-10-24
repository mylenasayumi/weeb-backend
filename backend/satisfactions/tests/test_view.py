from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from satisfactions.models import Satisfaction

User = get_user_model()


class SatisfactionsViewTests(APITestCase):
    """
    Unit tests for the SatisfactionAPIView.
    """

    def setUp(self):
        """
        Create example of satisfactions.
        """
        self.user = User.objects.create_user(
            email="john@example.com",
            password="pass12345",
            first_name="John",
            last_name="Doe",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.satisfaction = Satisfaction.objects.create(
            polarity=1, description="Great experience!", user=self.user
        )

        self.list_url = reverse("satisfactions-list")
        self.detail_url = lambda pk: reverse("satisfactions-detail", args=[pk])

    ############ CREATE ############
    def test_create_satisfaction_success(self):
        """
        Should create a new satisfaction form when valid data is provided.
        """
        data = {"polarity": 1, "description": "Good service!"}
        response = self.client.post(self.list_url, data=data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Satisfaction.objects.count(), 2)

    def test_create_satisfaction_invalid_rating_failure(self):
        """
        Should reject a satisfaction form with invalid data.
        """
        data = {"polarity": 9, "description": "Invalid rating"}
        response = self.client.post(self.list_url, data=data, format="json")
        self.assertEqual(response.status_code, 400)
