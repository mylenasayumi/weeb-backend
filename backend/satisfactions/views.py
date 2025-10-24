from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView

from .models import Satisfaction
from .serializers import SatisfactionSerializer

class SatisfactionViewSet(CreateAPIView):
    """
    View to save a satisfaction comment in the database.
    Handle CRUD operations on Satisfactions : list / retrieve / create / update / partial_update / destroy
    """

    queryset = Satisfaction.objects.all()
    serializer_class = SatisfactionSerializer
    
    def perform_create(self, serializer):
        """
        Associate the current authentified user
        """
        serializer.save(user=self.request.user)
