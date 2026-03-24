from rest_framework import serializers

from .models import Like


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["id", "article", "created_at"]
        depth = 1
