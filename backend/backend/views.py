import logging

from rest_framework_simplejwt.views import TokenObtainPairView

logger = logging.getLogger("auth")


class MyTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        ip = request.META.get("REMOTE_ADDR")

        try:
            response = super().post(request, *args, **kwargs)
            logger.info(f"JWT token obtained for email={email} from ip={ip}")
        except:
            logger.warning(f"Failed JWT login for email={email} from ip={ip}")
            raise

        return response


import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class GithubLoginRedirectView(APIView):
    """Redirige l'user vers GitHub pour autorisation"""

    permission_classes = [AllowAny]

    def get(self, request):
        github_auth_url = (
            f"https://github.com/login/oauth/authorize"
            f"?client_id={settings.GITHUB_CLIENT_ID}"
            f"&redirect_uri={settings.GITHUB_CALLBACK_URL}"
            f"&scope=user:email"
        )
        return redirect(github_auth_url)


class GithubCallbackView(APIView):
    """Reçoit le code GitHub, crée/récupère le user, renvoie un JWT"""

    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get("code")
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
        print("github_user = ", github_user, flush=True)

        email = github_user.get("email")
        print("111 email ? ", email, flush=True)
        if not email:

            emails_response = requests.get(
                "https://api.github.com/user/emails", headers=headers
            )
            emails = emails_response.json()
            print("emails ? ", emails, flush=True)
            primary = next(
                (e for e in emails if e.get("primary") and e.get("verified")), None
            )
            email = primary["email"] if primary else None

        print(" 222 email ? ", email, flush=True)

        if not email:
            return redirect(f"{settings.FRONTEND_URL}/login?error=no_email")

        name = github_user.get("name") or github_user.get("login") or ""
        parts = name.split(" ", 1)
        print("name = ", name, flush=True)
        print("parts = ", parts, flush=True)
        print('github_user.get("name")  = ', github_user.get("name"), flush=True)
        print('github_user.get("login")  = ', github_user.get("login"), flush=True)
        print("name = ", name, flush=True)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "is_active": False,
            },
        )

        print("is_active ? ", user.is_active, flush=True)
        # Si le user existait mais était inactif, on l'active
        if not user.is_active:
            user.is_active = False

        print("ON A LE USER ? ", user, flush=True)
        user.save()

        refresh = RefreshToken.for_user(user)
        refresh["user_email"] = user.email

        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        print("ici fin ", access_token, refresh_token)
        return redirect(
            f"{settings.FRONTEND_URL}/auth/callback"
            f"?access={access_token}&refresh={refresh_token}"
        )
