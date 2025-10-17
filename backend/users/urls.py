from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, index

# Router pour les endpoints /api/users/, /api/users/{id}/, etc.
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Vue d’accueil accessible à /api/
    path("", index, name="index"),
]

# Ajout des routes du ViewSet
urlpatterns += router.urls
