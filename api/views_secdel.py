from rest_framework import viewsets
from vote.models_secdel import SecDel
from api.serializers_secdel import SecDelSerializer
from rest_framework.permissions import IsAuthenticated

#    API ViewSet for managing Sec-Del records.
class SecDelViewSet(viewsets.ModelViewSet):
    queryset = SecDel.objects.all()
    serializer_class = SecDelSerializer
    permission_classes = [IsAuthenticated]              # asks for authentication