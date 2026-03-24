from articles.models import Article
from django.shortcuts import get_object_or_404
from likes.models import Like
from likes.serializers import LikeSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


class LikeViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Retrieve all likes from a user.
        """
        likes = Like.objects.filter(user=request.user)
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="toggle")
    def toggle(self, request, pk=None):
        """
        Allow a user to like an article.
        """
        article = get_object_or_404(Article, id=pk)

        like = Like.objects.filter(user=request.user, article=article).first()

        if like:
            like.delete()
            return Response(
                {"liked": False, "message": "Like removed"}, status=status.HTTP_200_OK
            )

        Like.objects.create(user=request.user, article=article)

        return Response(
            {"liked": True, "message": "Article liked"}, status=status.HTTP_201_CREATED
        )
