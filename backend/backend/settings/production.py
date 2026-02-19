import os

import dj_database_url

from backend.settings.base import *

# ==============================================================================
# SÉCURITÉ
# ==============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-dev-secret-ci")

DEBUG = os.getenv("DEBUG", False)

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")

# ==============================================================================
# BASE DE DONNÉES
# ==============================================================================

DATABASES = {"default": dj_database_url.config(conn_max_age=600, ssl_require=True)}

# ==============================================================================
# FICHIERS STATIQUES (WHITENOISE)
# ==============================================================================

STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
