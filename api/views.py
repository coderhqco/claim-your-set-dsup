from telnetlib import AUTHENTICATION
from rest_framework import viewsets
from vote.models import Districts
from api import serializers as apiSerializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class DistrictsViewSet(viewsets.ModelViewSet):
    queryset = Districts.objects.all()
    serializer_class = apiSerializers.DistrictsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]