from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Satisfaction
from .serializers import SatisfactionSerializer

class SatisfactionAPIView(APIView):
    """
    ViewSet to save a satisfaction comment in the database.
    Handle CRUD operations on Satisfactions : list / retrieve / create / update / partial_update / destroy
    """

    queryset = Satisfaction.objects.all()
    serializer_class = SatisfactionSerializer

    def post(self, request):
        serializer = SatisfactionSerializer(data=request.data)

        if serializer.is_valid():
            # Save in the database
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_create(self, serializer):
        """
        Associate the current authentified user
        """
        serializer.save(user=self.request.user)
