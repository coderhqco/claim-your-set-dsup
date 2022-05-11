from rest_framework import serializers
from vote.models import Districts
class DistrictsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Districts
        fields = [ 'name', 'code']
    