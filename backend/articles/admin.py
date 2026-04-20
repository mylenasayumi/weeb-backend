from django.contrib import admin

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "views", "created_at")
    search_fields = (
        "title",
        "description",
        "user__email",
        "user__first_name",
        "user__last_name",
    )
    list_filter = ("created_at",)
    ordering = ("-created_at",)
