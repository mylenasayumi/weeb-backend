from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import EmailUser


@admin.register(EmailUser)
class UserAdmin(BaseUserAdmin):
    # Default ordering
    ordering = ("email",)
    
    # Columns displayed
    list_display = ("id", "email", "first_name", "last_name", "is_staff", "is_superuser", "is_active")
    
    # Fields to search by
    search_fields = ("email", "first_name", "last_name")

    # Filters show on the right sidebar
    list_filter = ("is_staff", "is_superuser", "is_active")


    # Update form for creating a user or a superuser
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2", "is_staff", "is_superuser"),
        }),
    )
