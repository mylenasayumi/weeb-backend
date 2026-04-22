"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.development")
print("DJANGO_SETTINGS_MODULE: test", os.environ.get("DJANGO_SETTINGS_MODULE"))
print(
    "DJANGO_SETTINGS_MODULE: test", os.environ.get("DJANGO_SETTINGS_MODULE"), flush=True
)

application = get_wsgi_application()
