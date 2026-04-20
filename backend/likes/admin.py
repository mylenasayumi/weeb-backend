from django.contrib import admin

from .models import Like


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "article")
    search_fields = ("user__email", "article__title")
    ordering = ("-id",)
