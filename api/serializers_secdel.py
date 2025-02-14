from rest_framework import serializers
from vote.models_secdel import SecDel

class SecDelSerializer(serializers.ModelSerializer):
    circle = serializers.StringRelatedField()                       #displays the Circle code instead of ID
    user = serializers.StringRelatedField()                         #displays the username instead of ID

    class Meta:
        model = SecDel
        fields = ['id', 'circle', 'user', 'created_at', 'updated_at']