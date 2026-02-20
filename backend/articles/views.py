import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import Article
from .permissions import IsOwnerOrAdminOrReadOnly
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

    permission_classes = [IsOwnerOrAdminOrReadOnly]

    def perform_create(self, serializer):
        """
        Associate the current authentified user
        """
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Override default Update() function for monitoring purposes.
        """
        article = self.get_object()
        ip = request.META.get("REMOTE_ADDR")
        email = request.user.email

        response = super().update(request, *args, **kwargs)
        logger.info(f"Article updated: id={article.id} by email={email} from ip={ip}")

        return response

    def partial_update(self, request, *args, **kwargs):
        """
        Override default PartialUpdate() function for monitoring purposes.
        """
        article = self.get_object()
        ip = request.META.get("REMOTE_ADDR")
        email = request.user.email

        response = super().partial_update(request, *args, **kwargs)
        logger.info(
            f"Article partially updated: id={article.id} by email={email} from ip={ip}"
        )

        return response
