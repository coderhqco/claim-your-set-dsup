

from rest_framework import serializers
from api import models as apiModels
from django.contrib.auth.models import User


class SecDelSerializer(serializers.ModelSerializer):
    class Meta:
        model = apiModels.SecDelModel
        fields = "__all__"