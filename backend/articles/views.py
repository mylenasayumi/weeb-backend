import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import Article
from .serializers import ArticleSerializer


logger = logging.getLogger("articles")

class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing articles via API.
    list : paginated list of articles / retrieve : article details / create : registration / update : modification / partial_update : partial modification / destroy : deletion.
    """

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = ["title", "user"]
    search_fields = [
        "title",
        "description",
        "user__email",
        "user__first_name",
        "user__last_name",
    ]
    ordering_fields = ["title", "user"]
    ordering = ["title"]

    def perform_create(self, serializer):
        """
        Associate the current authentified user
        """
        serializer.save(user=self.request.user)

    def get_permissions(self):
        """
        Set permissions :
            list / retrieve for everyone
            update / create / destroy for authenticated and owner OR admin
        """
        if self.action in ["create", "destroy", "update", "partial_update"]:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_object(self):
        """
        Check if user is the owner of article or is admin.
        """
        obj = super().get_object()
        if not self.request.user.is_staff and obj.user != self.request.user:
            raise permissions.exceptions.PermissionDenied(
                "You are not authorized to modify this article."
            )
        return obj

    def update(self, request, *args, **kwargs):
        article = self.get_object()
        ip = request.META.get("REMOTE_ADDR")
        email = request.user.email

        response = super().update(request, *args, **kwargs)
        logger.info(f"Article updated: id={article.id} by email={email} from ip={ip}")

        return response

    def partial_update(self, request, *args, **kwargs):
        article = self.get_object()
        ip = request.META.get("REMOTE_ADDR")
        email = request.user.email

        response = super().partial_update(request, *args, **kwargs)
        logger.info(f"Article partially updated: id={article.id} by email={email} from ip={ip}")

        return response
