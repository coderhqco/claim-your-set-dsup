from rest_framework import serializers
from api.serializers import UserSerializer
from bills import models as billModels


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = billModels.Bill
        fields = "__all__" 


class BillVoteSerializer(serializers.ModelSerializer):
    bill = BillSerializer()
    voter = UserSerializer()
    class Meta:
        model = billModels.BillVote
        fields = ["bill","voter","voted_by_fDel","your_vote","vote_date","last_update"]