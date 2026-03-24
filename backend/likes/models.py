from articles.models import Article
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Like(models.Model):
    """
    Model to represent a like.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("user", "article")

    def __str__(self):
        return f"Like from: {self.user.email} on article: {self.article.title}"
