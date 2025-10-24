from unittest.mock import patch
import unittest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from satisfactions.models import Satisfaction
import os
User = get_user_model()
from rest_framework import status


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

        self.list_url = reverse("satisfactions_create")

        self.detail_url = lambda pk: reverse("satisfactions-detail", args=[pk])

    ############ CREATE ############
    @unittest.skipIf(os.getenv("CI") == "true", "Skip test because no pkl files are pushed")
    @patch("satisfactions.serializers.detect", return_value="fr")
    def test_create_satisfaction_fr_success(self, mock_detect):
        """
        Should create a new satisfaction form when valid data is provided.
        """
        data = {
            "description": "je parle français et ça marche",
            "email": "user@user.com",
            "first_name": "user",
            "last_name": "user",
        }

        response = self.client.post(self.list_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Satisfaction.objects.count(), 2)

    @unittest.skipIf(os.getenv("CI") == "true", "Skip test because no pkl files are pushed")
    @patch("satisfactions.serializers.detect", return_value="en")
    def test_create_satisfaction_en_success(self, mock_detect):
        """
        Should create a new satisfaction form when valid data is provided.
        """
        data = {
            "description": "I love you, you are so beautiful",
            "email": "user@user.com",
            "first_name": "user",
            "last_name": "user",
        }

        response = self.client.post(self.list_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Satisfaction.objects.count(), 2)

    @unittest.skipIf(os.getenv("CI") == "true", "Skip test because no pkl files are pushed")
    @patch("satisfactions.serializers.detect", return_value="fr")
    @patch("satisfactions.serializers.os.path.isfile", return_value=False)
    def test_create_satisfaction_missing_model_fr_failure(
        self, mock_isfile, mock_detect
    ):
        """
        Should return 400 if the model file is missing for French language.
        """
        self.client.force_authenticate(user=self.user)

        data = {
            "description": "je parle français et ça marche",
            "email": "user@user.com",
            "first_name": "user",
            "last_name": "user",
        }

        response = self.client.post(self.list_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Sorry we can not know", str(response.data))

    @unittest.skipIf(os.getenv("CI") == "true", "Skip test because no pkl files are pushed")
    @patch("satisfactions.serializers.detect", return_value="en")
    @patch("satisfactions.serializers.os.path.isfile", return_value=False)
    def test_create_satisfaction_missing_model_en_failure(
        self, mock_isfile, mock_detect
    ):
        """
        Should return 400 if the model file is missing for English language.
        """
        self.client.force_authenticate(user=self.user)

        data = {
            "description": "Bryan is in the kitchen",
            "email": "user@user.com",
            "first_name": "user",
            "last_name": "user",
        }

        response = self.client.post(self.list_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Sorry we can not know", str(response.data))
