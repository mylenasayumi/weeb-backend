from .models import Article
from .serializers import ArticleSerializer
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing articles via API. 
    list : paginated list of articles / retrieve : article details / create : registration / update : modification / partial_update : partial modification / destroy : deletion.
    """
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = ['title', 'user']
    search_fields = ['title', 'description', 'user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['title', 'user']
    ordering = ['title']

    def perform_create(self, serializer):
        """
        Associate the current authentified user
        """
        serializer.save(user=self.request.user)