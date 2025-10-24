from rest_framework import serializers

from .models import Satisfaction


class SatisfactionSerializer(serializers.ModelSerializer):
    """
    Serializer to convert Satisfaction objects to JSON.
    Custom validations for fields.
    """

    class Meta:
        model = Satisfaction
        fields = ["email", "last_name", "first_name", "description", "user"]
        extra_kwargs = {"user": {"read_only": True}}

    def validate_email(self, value):
        """
        Ensures that the email is not empty or composed only of spaces.
        """
        if not value.strip():
            raise serializers.ValidationError("Email cannot be empty.")
        return value

    def validate_description(self, value):
        """
        Ensures that the description is not empty or composed only of spaces.
        Ensures that the description has at least 10 characters.
        """
        if not value.strip():
            raise serializers.ValidationError("Description cannot be empty.")
        elif len(value) < 10:
            raise serializers.ValidationError(
                "The description must contain at least 10 characters."
            )
        return value
