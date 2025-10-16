from django.contrib import admin  # Import du module admin de Django
from .models import User  # Import du modèle User personnalisé


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Ordre d'affichage par défaut dans l'admin (par email)
    ordering = ("email",)
    # Colonnes affichées dans la liste des utilisateurs
    list_display = ("email", "first_name", "last_name")
    # Champs sur lesquels la recherche est possible dans l'admin
    search_fields = ("email", "first_name", "last_name")

    # Organisation des champs dans le formulaire de modification d'un utilisateur
    fields = ("email", "first_name", "last_name", "password")
