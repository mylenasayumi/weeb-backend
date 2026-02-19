import importlib
import unittest
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase


class SettingsCITest(unittest.TestCase):
    def test_ci_database_settings(self):
        with mock.patch.dict("os.environ", {"CI": "true"}):
            settings = importlib.reload(
                importlib.import_module("backend.settings.development")
            )
            self.assertEqual(
                settings.DATABASES["default"]["ENGINE"], "django.db.backends.sqlite3"
            )
            self.assertEqual(settings.DATABASES["default"]["NAME"], ":memory:")


class SettingsCoverageTest(SimpleTestCase):
    def test_static_and_auth_settings(self):
        assert settings.LANGUAGE_CODE == "en-us"
        assert settings.TIME_ZONE == "UTC"
        assert settings.STATIC_URL == "/static/"
        assert settings.DEFAULT_AUTO_FIELD == "django.db.models.BigAutoField"
        assert settings.CORS_ALLOW_ALL_ORIGINS is True # TEST to mock for prod ?
        assert settings.AUTH_USER_MODEL == "users.EmailUser"
        assert settings.AUTHENTICATION_BACKENDS == ["users.backend.EmailBackend"]
