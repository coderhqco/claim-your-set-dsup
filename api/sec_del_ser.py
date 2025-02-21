from rest_framework import serializers
from api import models as apiModels
from api.serializers import DistrictsSerializer, UserSerializer

class SecDelSerializer(serializers.ModelSerializer):
    district = DistrictsSerializer()
    is_active= serializers.ReadOnlyField()
    class Meta:
        model = apiModels.SecDelModel
        fields = "__all__"


class SecDelMembersSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    sec_del = SecDelSerializer()
    class Meta:
        model = apiModels.SecDelMembers
        fields = "__all__"