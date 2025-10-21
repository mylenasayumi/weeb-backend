from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer to convert Article objects to JSON.
    Custom validations for fields.
    """
    class Meta:
        model = Article
        fields = ['id', 'title', 'description', 'image', 'user']
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def validate_title(self, value):
        """
        Ensures that the title has at least 5 characters.
        """
        if len(value) < 5:
            raise serializers.ValidationError("The title must contain at least 5 characters.")
        return value

    def validate_description(self, value):
        """
        Ensures that the description is not empty or composed only of spaces.
        """
        if not value.strip():
            raise serializers.ValidationError("Description cannot be empty.")
        return value
