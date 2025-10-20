
from rest_framework import serializers
from django.contrib.auth import get_user_model

# Récupère le modèle User défini dans models.py
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    # Sérialiseur pour afficher ou modifier un utilisateur existant.
    # N'expose pas le mot de passe (hash) dans les réponses API.
    
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]


class UserCreateSerializer(serializers.ModelSerializer):
    
    # Sérialiseur pour la création d'un utilisateur (inscription).
    # Le mot de passe est demandé en clair, puis hashé avant sauvegarde.
    
    password = serializers.CharField(write_only=True, min_length=8)  # Champ password non exposé en lecture

    class Meta:
        model = User  # Modèle utilisé
        fields = ["email", "first_name", "last_name", "password"]

    def create(self, validated_data):
        # Récupère et retire le mot de passe des données validées
        password = validated_data.pop("password")
        # Crée l'utilisateur sans le mot de passe
        user = User(**validated_data)
        # Hash le mot de passe et l'associe à l'utilisateur
        user.set_password(password)
        user.save()
        return user
