from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Satisfaction
from .serializers import SatisfactionSerializer


class SatisfactionView(CreateAPIView):
    """
    View to save a satisfaction comment in the database.
    Handle CRUD operations on Satisfactions : list / retrieve / create / update / partial_update / destroy
    """

    queryset = Satisfaction.objects.all()
    serializer_class = SatisfactionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Associate the current authentified user
        """
        serializer.save(user=self.request.user)
