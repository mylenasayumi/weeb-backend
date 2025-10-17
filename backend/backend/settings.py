from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager, Permission
)
from django.core.validators import RegexValidator, MaxLengthValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Manager custom avec email comme identifiant principal."""

    def create_user(self, email, password=None, first_name="", last_name="", **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not password:
            raise ValueError("Password is required")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields,
        )
        user.set_password(password)  # hash du mot de passe
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, first_name="", last_name="", **extra_fields):
        """Crée un superuser utilisable dans l'admin."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, first_name, last_name, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """User personnalisé : email unique, prénom, nom, états, etc."""

    # Validateur de format email (en plus d'EmailField)
    email_validator = RegexValidator(
        regex=r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$",
        message="Email invalide."
    )

    # Identifiant principal
    email = models.EmailField(unique=True, validators=[email_validator], db_index=True)

    # Infos de profil
    first_name = models.CharField(max_length=50, validators=[MaxLengthValidator(50)], blank=True)
    last_name = models.CharField(max_length=50, validators=[MaxLengthValidator(50)], blank=True)

    # Champs requis par l'admin / permissions
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Métadonnées
    date_joined = models.DateTimeField(default=timezone.now)

    # Redéfinition explicite pour contrôler le related_name
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='+',  # empêche de créer une relation inverse sur Permission
    )

    # Manager
    objects = UserManager()

    # Auth config
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # pas d'autres champs obligatoires pour createsuperuser

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.email
