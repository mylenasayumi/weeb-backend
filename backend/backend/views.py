import logging
import secrets
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
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

        referer = request.headers.get("Referer", "")
        parsed = urlparse(referer)
        request_origin = f"{parsed.scheme}://{parsed.netloc}"

        if not settings.CORS_ALLOW_ALL_ORIGINS:
            if (
                not request_origin
                or request_origin not in settings.CORS_ALLOWED_ORIGINS
            ):
                return Response(
                    {"error": "Unauthorized origin"}, status=status.HTTP_403_FORBIDDEN
                )

        request.session["github_oauth_frontend"] = request_origin

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
        frontend_url = request.session.get("github_oauth_frontend")

        if not frontend_url:
            return Response(
                {"error": "Unauthorized origin"}, status=status.HTTP_403_FORBIDDEN
            )
        if frontend_url not in settings.CORS_ALLOWED_ORIGINS:
            return Response(
                {"error": "Unauthorized origin"}, status=status.HTTP_403_FORBIDDEN
            )

        if not returned_state or returned_state != saved_state:
            return redirect(f"{frontend_url}/login?error=invalid_state")

        request.session.pop("github_oauth_state", None)
        if not code:
            return redirect(f"{frontend_url}/login?error=no_code")

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
            return redirect(f"{frontend_url}/login?error=token_failed")

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
            return redirect(f"{frontend_url}/login?error=no_email")

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

        temp_code = secrets.token_urlsafe(32)
        cache.set(
            f"oauth_temp:{temp_code}",
            {"access": access_token, "refresh": refresh_token},
            timeout=300,
        )

        return redirect(f"{frontend_url}/auth/callback?code={temp_code}")


class ExchangeOauthCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response({"error": "Missing code"}, status=400)

        cache_key = f"oauth_temp:{code}"
        tokens = cache.get(cache_key)

        if not tokens:
            return Response({"error": "Invalid or expired code"}, status=400)

        cache.delete(cache_key)

        response = Response({"access": tokens["access"]})
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh"],
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
            path="/",
        )
        return response
