from rest_framework.throttling import SimpleRateThrottle


class PasswordResetThrottle(SimpleRateThrottle):
    """
    Custom throttle class for password reset requests.
    It limits the number of password reset requests that can be made for a given email address and IP address combination.
    """

    scope = "password_reset"

    def get_cache_key(self, request, view):
        email = request.data.get("email")
        if not email:
            return None

        ident = self.get_ident(request)
        return f"password_reset_{email.lower().strip()}_{ident}"
