from django.urls import path

from . import views

urlpatterns = [
    path("", views.article_create_read_list, name="article_create_read_list"),
]