from rest_framework import viewsets
from vote.models import Districts
from api import serializers as apiSerializers

class DistrictsViewSet(viewsets.ModelViewSet):
    queryset = Districts.objects.all()
    serializer_class = apiSerializers.DistrictsSerializer