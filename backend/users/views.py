from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import UserCreateSerializer, UserSerializer

User = get_user_model()


class IsSelf(permissions.BasePermission):
    """
    Custom permission that allows users to access/modify their own data.
    """

    def has_object_permission(self, request, view, obj):
        return obj.id == getattr(request.user, "id", None)


class UserViewSet(viewsets.ModelViewSet):
    """
    Handle CRUD operations on USERS
        list/retrieve
        create
        update/partial_update/destroy
        me
    """

    queryset = User.objects.all().order_by("-id")
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "me":
            return [permissions.IsAuthenticated()]
        elif self.action in ["partial_update", "update", "destroy"]:
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=["get"])
    def me(self, request):
        """
        GET /api/users/me
        Returns the profil of the current user
        """
        return Response(UserSerializer(request.user).data)
