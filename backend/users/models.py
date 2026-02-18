from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .managers import EmailUserManager


class EmailUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True, max_length=50, db_index=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    # User our EmailUserManager
    objects = EmailUserManager()

    def __str__(self):
        return f"User email: {self.email}, created at: {self.created_at}."
