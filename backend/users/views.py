import logging

from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import UserCreateSerializer, UserSerializer

User = get_user_model()
logger = logging.getLogger("users")


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

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        ip = request.META.get("REMOTE_ADDR")

        try:
            response = super().create(request, *args, **kwargs)
            logger.info(f"User created: email={email} from ip={ip}")
        except:
            logger.warning(f"Failed user created for email={email} from ip={ip}")
            raise

        return response
