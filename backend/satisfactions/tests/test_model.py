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
            email="john@example.com",
            first_name="John",
            last_name="Doe",
            description="Great experience!",
            user=self.user,
            polarity=True
        )

    def test_get_str_success(self):
        """
        Test __str__ method returns correct string
        """
        expected_output = f"Satisfaction Form: {self.satisfaction.first_name} {self.satisfaction.last_name} sent a satisfaction comment on {self.satisfaction.created_at}."
        self.assertEqual(self.satisfaction.__str__(), expected_output)
