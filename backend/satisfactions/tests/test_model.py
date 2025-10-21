from django.test import TestCase
from satisfactions.models import Satisfaction
from django.contrib.auth import get_user_model

User = get_user_model()

class SatisfactionsModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="john@example.com", 
            password="pass12345",
            first_name="John",
            last_name="Doe"
        )

        self.satisfaction = Satisfaction.objects.create(
            polarity=1,
            description="Great experience!",
            user=self.user
        )

    def test_get_str_success(self):
        """
        Test __str__ method returns correct string
        """
        expected_output = f"Polarity: {self.satisfaction.polarity} - {self.satisfaction.description}"
        self.assertEqual(self.satisfaction.__str__(), expected_output)
