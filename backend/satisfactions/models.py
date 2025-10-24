from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Satisfaction(models.Model):
    """
    Model to represent a satisfaction form sent by user.
    """

    email = models.EmailField()
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    polarity = models.BooleanField()

    def __str__(self):
        """
        Display, first and last name of the user and created_at date.
        """
        return f"Satisfaction Form: {self.first_name} {self.last_name} sent a satisfaction comment on {self.created_at}."
