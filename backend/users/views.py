import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
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
from .throttling import PasswordResetThrottle

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
        except Exception as e:
            logger.warning(f"Failed user created for email={email} from ip={ip}: {e}")
            raise

        if email:
            send_mail(
                subject="WEEB - Welcome",
                message=f"Your account is successfully created.\n Please wait your approval.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
        return response


class RequestPasswordResetEmailView(generics.GenericAPIView):
    """
    Handle password reset requests
    POST /api/users/password-reset/request/
    """

    serializer_class = PasswordResetRequestSerializer
    throttle_classes = [PasswordResetThrottle]
    permission_classes = [permissions.AllowAny]

    def post(self, request):

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data["email"]
            user = User.objects.filter(email=email).first()

            logger.info(f"RequestPasswordResetEmailView")
            logger.info(f"{email}")
            logger.info(f"{user}")

            if user:
                # Generate token
                uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)

                request_origin = request.headers.get("Origin")
                referer = request.headers.get("Referer")
                logger.info(f" referer {referer}")
                logger.info(f" request_origin {request_origin}")
                logger.info(f" CORS_ALLOWED_ORIGINS {settings.CORS_ALLOWED_ORIGINS}")
                # prod
                if settings.CORS_ALLOW_ALL_ORIGINS == False:
                    if (
                        not request_origin
                        or request_origin not in settings.CORS_ALLOWED_ORIGINS
                    ):
                        return Response(
                            {"error": "Unauthorized origin"},
                            status=status.HTTP_403_FORBIDDEN,
                        )

                reset_url = (
                    f"{request_origin}/reset-password?uidb64={uidb64}&token={token}"
                )
                logger.info(f" reset_url {reset_url}")
                send_mail(
                    subject="WEEB - Reset your password",
                    message=f"Click here to reset your password: {reset_url}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,
                )

                logger.info(f"Password reset requested for email={user.email}")
                logger.debug(f"Reset link: {reset_url}")

        except Exception as e:
            logger.warning(f"errur : {e}")

            raise

        # Always returns the same response, regardless of whether the user exists or not.
        return Response(
            {
                "message": "If an account is associated with this email, you will receive instructions to reset your password."
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Handle password reset confirmation
    POST /api/users/password-reset/confirm/?uidb64=xxx&token=xxx
    """

    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]
        uidb64 = request.query_params.get("uidb64")

        if not uidb64:
            return Response(
                {"error": "Missing uidb64 parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)

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

        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response(
                {"error": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST
            )
