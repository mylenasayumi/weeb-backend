
# Import des modules DRF nécessaires pour les vues, permissions et réponses API
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
# Import du modèle User personnalisé
from django.contrib.auth import get_user_model
# Import des serializers pour User
from .serializer import UserSerializer, UserCreateSerializer

# Récupère le modèle User défini dans models.py
User = get_user_model()

class IsSelf(permissions.BasePermission):
    
    # Permission personnalisée : autorise la modification ou suppression uniquement si l'utilisateur est lui-même.
    
    def has_object_permission(self, request, view, obj):
        # Vérifie que l'utilisateur connecté correspond à l'objet User ciblé
        return obj.id == getattr(request.user, "id", None)

class UserViewSet(viewsets.ModelViewSet):

    # ViewSet principal pour gérer les utilisateurs via l'API. ( list : liste paginée des utilisateurs / retrieve : détails d'un utilisateur /create : inscription )

    # Récupère tous les utilisateurs, triés par id décroissant
    queryset = User.objects.all().order_by("-id")
    # Permissions par défaut : lecture ouverte
    permission_classes = [permissions.AllowAny]
    # Sérialiseur par défaut
    serializer_class = UserSerializer

    def get_permissions(self):

        #  Définit les permissions selon l'action demandée. ( create : tout le monde peut s'inscrire / update/destroy : interdit à tout le monde / autres : lecture ouverte )
        if self.action == "create":
            return [permissions.AllowAny()]
        elif self.action in ["partial_update", "update", "destroy"]:
            # Interdit la modification et suppression du compte
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        else:
            return [permissions.AllowAny()]

    def get_serializer_class(self):

        # Utilise un serializer différent pour la création (inscription).

        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):

        # Endpoint personnalisé : /users/me/ - Renvoie le profil de l'utilisateur actuellement connecté.
    
        return Response(UserSerializer(request.user).data)
    
