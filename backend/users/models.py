from django.db import models  
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)  # Import des classes nécessaires pour un user custom
from django.core.validators import RegexValidator, MaxLengthValidator  # Pour valider email et longueur


class UserManager(BaseUserManager):
    
    # Manager custom pour créer des utilisateurs avec email comme identifiant principal.
   
    def create_user(self, email, password=None, first_name="", last_name="", **extra_fields):
        # Vérifie que l'email est fourni
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)

        # Crée une instance User avec les champs fournis
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        # Vérifie que le mot de passe est fourni
        if not password:
            raise ValueError("Password is required")
        user.set_password(password)  # Hash du mot de passe
        user.save(using=self._db)
        return user




class User(AbstractBaseUser, PermissionsMixin):

    # Modèle utilisateur personnalisé : email unique, prénom, nom, mot de passe hashé, droits, etc. 
    # Hérite de AbstractBaseUser pour la gestion du mot de passe et PermissionsMixin pour les droits.
  
    # Validateur regex pour le format de l'email
    email_validator = RegexValidator(
        regex=r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$",
        message="Email invalide."
    )

    # Email unique, utilisé comme identifiant principal
    email = models.EmailField(
        unique=True,
        validators=[email_validator],
        db_index=True
    )
    # Prénom et nom de famille de l'utilisateur (max 50 caractères)
    first_name = models.CharField(max_length=50, validators=[MaxLengthValidator(50)])
    last_name = models.CharField(max_length=50, validators=[MaxLengthValidator(50)])


    # Lien avec le manager custom
    objects = UserManager()

    # Utilisation de l'email comme identifiant principal
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Pas d'autres champs obligatoires pour createsuperuser


    class Meta:
        verbose_name = "user"  # Nom affiché dans l'admin
        verbose_name_plural = "users"

    def __str__(self):
        # Affichage de l'utilisateur (email) dans l'admin et le shell
        return self.email
