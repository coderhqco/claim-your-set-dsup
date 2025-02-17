from rest_framework import serializers
from api import models as apiModels
from api.serializers import DistrictsSerializer

class SecDelSerializer(serializers.ModelSerializer):
    district = DistrictsSerializer()
    class Meta:
        model = apiModels.SecDelModel
        fields = "__all__"