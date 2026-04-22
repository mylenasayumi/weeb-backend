import importlib
from unittest import mock

from django.conf import settings


def test_ci_database_settings():
    """
    Should use SQLite in memory when CI environment variable is set.
    """
    with mock.patch.dict("os.environ", {"CI": "true"}):
        ci_settings = importlib.reload(
            importlib.import_module("backend.settings.development")
        )
    assert ci_settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3"
    assert ci_settings.DATABASES["default"]["NAME"] == ":memory:"


def test_static_and_auth_settings():
    """
    Should have correct static and auth settings.
    """
    assert settings.LANGUAGE_CODE == "en-us"
    assert settings.TIME_ZONE == "UTC"
    assert settings.STATIC_URL == "/static/"
    assert settings.DEFAULT_AUTO_FIELD == "django.db.models.BigAutoField"
    assert settings.AUTH_USER_MODEL == "users.EmailUser"
    assert settings.AUTHENTICATION_BACKENDS == ["users.backend.EmailBackend"]


def test_production_settings():
    """
    Should have correct production settings.
    """
    with mock.patch.dict(
        "os.environ",
        {
            "DEBUG": "False",
            "ALLOWED_HOSTS": "example.com, www.example.com",
        },
    ):
        prod_settings = importlib.reload(
            importlib.import_module("backend.settings.production")
        )

    assert prod_settings.DEBUG == False
    assert len(prod_settings.ALLOWED_HOSTS) == 2
    assert prod_settings.CORS_ALLOW_ALL_ORIGINS == False
    assert prod_settings.SESSION_COOKIE_SECURE == True
    assert prod_settings.CSRF_COOKIE_SECURE == True
    assert len(prod_settings.ALLOWED_FRONTEND_URLS) == 1
