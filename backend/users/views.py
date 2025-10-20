# DRF
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

# Django
from django.http import HttpResponse
from django.contrib.auth import get_user_model

# Serializers
from .serializer import UserSerializer, UserCreateSerializer

User = get_user_model()


class IsSelf(permissions.BasePermission):
    """
    Permission personnalisée : autorise l'accès objet seulement à lui-même.
    (Non utilisée dans la config actuelle où l’update/destroy sont réservés admin.)
    """
    def has_object_permission(self, request, view, obj):
        return obj.id == getattr(request.user, "id", None)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet principal pour gérer les utilisateurs via l’API.
    - list/retrieve : lecture ouverte
    - create : inscription ouverte
    - update/partial_update/destroy : réservé aux admins (interdit aux users)
    """

    queryset = User.objects.all().order_by("-id")
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        elif self.action in ["partial_update", "update", "destroy"]:
            # réservé aux admins
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """GET /api/users/me/ — profil de l’utilisateur connecté."""
        return Response(UserSerializer(request.user).data)
