from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer to verify if a user is active before issuing tokens.
    Extends the default TokenObtainPairSerializer to add is_active validation.
    """

    def validate(self, attrs):
        """
        Validate that the user is active before returning tokens.
        """
        # Call the parent validate to get the tokens
        data = super().validate(attrs)

        try:
            user = User.objects.get(email=attrs["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid credentials."})

        # Check if user is active
        if not user.is_active:
            raise serializers.ValidationError(
                {
                    "detail": "User account is not active. Please contact an administrator."
                }
            )

        return data
