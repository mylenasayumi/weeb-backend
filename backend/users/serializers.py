from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    This serializer is used to represent user instance only for READ operations.
    """

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]


class UserCreateSerializer(serializers.ModelSerializer):
    """
    This serializer is used for user registration => WRITE operations.
    """

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password"]

    def create(self, validated_data):
        """
        Create a new user instance with hashed password.
        """
        password = validated_data.pop("password")

        user = User(**validated_data)

        user.set_password(password)
        user.save()
        return user
