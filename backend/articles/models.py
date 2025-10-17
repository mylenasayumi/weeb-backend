from django.db import models
from django.contrib.auth.models import User

class Article(models.Model):
    """
    Model to represent an article.
    """
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.URLField(max_length=500, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')

    def __str__(self):
        return self.title