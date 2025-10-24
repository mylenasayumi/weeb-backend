from django.test import TestCase
from rest_framework.exceptions import ValidationError
from satisfactions.serializers import SatisfactionSerializer

class SatisfactionSerializerTest(TestCase):
    def test_validate_email_empty_failure(self):
        serializer = SatisfactionSerializer(data={})
        with self.assertRaises(ValidationError):
            serializer.validate_email("   ")

    def test_validate_email_valid_failure(self):
        serializer = SatisfactionSerializer(data={})
        result = serializer.validate_email("test@example.com")
        self.assertEqual(result, "test@example.com")
    
    def test_validate_description_empty_failure(self):
        serializer = SatisfactionSerializer(data={})
        with self.assertRaises(ValidationError):
            serializer.validate_description("   ")

    def test_validate_description_too_small_failure(self):
        serializer = SatisfactionSerializer(data={})
        with self.assertRaises(ValidationError):
            serializer.validate_description("small")

    def test_validate_bad_language(self):
        serializer = SatisfactionSerializer(data={})
        with self.assertRaises(ValidationError):
            serializer.validate({'description': 'ich spreche deutch'})