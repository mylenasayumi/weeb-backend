import logging
import secrets

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

logger = logging.getLogger("auth")

User = get_user_model()


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as exc:
                logger.warning(f"Failed to blacklist refresh token: {exc}")
        response = Response({"detail": "Déconnecté."})
        response.delete_cookie("refresh_token", path="/")
        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        print("ICI PIERRE pas de refresh roken ", refresh_token, flush=True)
        if not refresh_token:
            return Response(
                {"detail": "Refresh token manquant."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        data = request.data.copy()
        data["refresh"] = refresh_token
        request._full_data = data

        try:
            response = super().post(request, *args, **kwargs)
        except (InvalidToken, TokenError) as e:
            print("LAAA probleme de response  ", response, flush=True)

            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        refresh_token = response.data.pop("refresh", None)
        if refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
                max_age=int(
                    settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
                ),
                path="/",
            )

        return response


class MyTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        ip = request.META.get("REMOTE_ADDR")

        try:
            response = super().post(request, *args, **kwargs)
            logger.info(f"JWT token obtained for email={email} from ip={ip}")
        except Exception as exc:
            logger.warning(f"Failed JWT login for email={email} from ip={ip}: {exc}")
            raise

        refresh_token = response.data.pop("refresh", None)
        if refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
                max_age=int(
                    settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
                ),
                path="/",
            )

        return response


class GithubLoginRedirectView(APIView):
    """
    Redirect user to Github page for authorization.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        state = secrets.token_urlsafe(32)

        request.session["github_oauth_state"] = state

        print("request.headers ", request.headers, flush=True)

        request_origin = request.headers.get("Origin")
        print("request_origin flush ", request_origin, flush=True)

        github_auth_url = (
            f"https://github.com/login/oauth/authorize"
            f"?client_id={settings.GITHUB_CLIENT_ID}"
            f"&redirect_uri={settings.GITHUB_CALLBACK_URL}"
            f"&scope=user:email"
            f"&state={state}"
        )
        return redirect(github_auth_url)


class GithubCallbackView(APIView):
    """
    Recieve the Github code, create user and send back access and refresh tokens
    """

    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get("code")
        returned_state = request.GET.get("state")
        saved_state = request.session.get("github_oauth_state")

        request_origin = request.headers.get("Origin")
        print("request_origin flush ", request_origin, flush=True)
        print("request_origin  ", request_origin)

        print("request.session ", request.session, flush=True)

        if not returned_state or returned_state != saved_state:
            return redirect(f"{settings.FRONTEND_URL}/login?error=invalid_state")

        request.session.pop("github_oauth_state", None)

        if not code:
            return redirect(f"{settings.FRONTEND_URL}/login?error=no_code")

        token_response = requests.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GITHUB_CALLBACK_URL,
            },
            headers={"Accept": "application/json"},
        )
        token_data = token_response.json()
        github_token = token_data.get("access_token")

        if not github_token:
            return redirect(f"{settings.FRONTEND_URL}/login?error=token_failed")

        headers = {"Authorization": f"Bearer {github_token}"}
        user_response = requests.get("https://api.github.com/user", headers=headers)

        github_user = user_response.json()
        email = github_user.get("email")

        if not email:
            emails_response = requests.get(
                "https://api.github.com/user/emails", headers=headers
            )
            emails = emails_response.json()
            primary = next(
                (e for e in emails if e.get("primary") and e.get("verified")), None
            )
            email = primary["email"] if primary else None

        if not email:
            return redirect(f"{settings.FRONTEND_URL}/login?error=no_email")

        name = github_user.get("name") or github_user.get("login") or ""
        parts = name.split(" ", 1)

        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""

        user, _ = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "is_active": True,
            },
        )

        user.is_active = True
        user.save()

        refresh = RefreshToken.for_user(user)
        refresh["user_email"] = user.email

        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = redirect(
            f"{settings.FRONTEND_URL}/auth/callback#access_token={access_token}"
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
            path="/",
        )

        return response
