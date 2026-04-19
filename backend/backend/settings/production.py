import os

import dj_database_url

from backend.settings.base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-dev-secret-ci")

DEBUG = os.getenv("DEBUG", False)

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")

# ==============================================================================
# DATABASE PRODUCTION
# ==============================================================================

DATABASES = {"default": dj_database_url.config(conn_max_age=600, ssl_require=True)}

# ==============================================================================
# STATIC FILES
# ==============================================================================

STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ==============================================================================
# Frontend URLs : should be set to the actual frontend URLs in production
# ==============================================================================

ALLOWED_FRONTEND_URLS = [
    "http://localhost:5173",  # Vite dev server
]

SESSION_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SAMESITE = "None"

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
