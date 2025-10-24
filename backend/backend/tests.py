import unittest
from unittest import mock
import importlib

class SettingsCITest(unittest.TestCase):
    def test_ci_database_settings(self):
        with mock.patch.dict("os.environ", {"CI": "true"}):
            settings = importlib.reload(importlib.import_module("backend.settings"))
            self.assertEqual(
                settings.DATABASES["default"]["ENGINE"],
                "django.db.backends.sqlite3"
            )
            self.assertEqual(
                settings.DATABASES["default"]["NAME"],
                ":memory:"
            )
