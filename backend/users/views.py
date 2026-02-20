import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes, smart_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserCreateSerializer,
    UserSerializer,
)

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


class RequestPasswordResetEmailView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email, is_active=True).first()

        if user:
            # Generate token
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            frontend_url = request.data.get("frontend_url", "http://localhost:5173")
            reset_url = f"{frontend_url}/reset-password?uidb64={uidb64}&token={token}"

            # Email sending simulation
            print(f"---- RESET EMAIL SENT TO {user.email} ----")
            print(f"Link: {reset_url}")
            print("------------------------------------------------------")

        # Always returns the same response, regardless of whether the user exists or not.
        return Response(
            {
                "message": "If an account is associated with this email, you will receive instructions to reset your password."
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]
        uidb64 = request.query_params.get("uidb64")

        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id, is_active=True)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {"error": "Invalid or expired token."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(password)
            user.save()

            return Response(
                {"message": "Password reset successfully."}, status=status.HTTP_200_OK
            )

        except Exception:
            return Response(
                {"error": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST
            )
