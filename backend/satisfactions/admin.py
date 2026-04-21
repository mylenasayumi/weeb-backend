from django.contrib import admin

from .models import Satisfaction


@admin.register(Satisfaction)
class SatisfactionAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "first_name", "last_name", "polarity", "created_at")
    search_fields = ("email", "first_name", "last_name", "description")
    list_filter = (
        "polarity",
        "created_at",
    )
    ordering = ("-created_at",)
