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
