from rest_framework import serializers
from api.serializers import UserSerializer
from bills import models as billModels


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = billModels.Bill
        fields = ["dtally","ntally","created_at","updated_at","congress","number","origin_chamber","origin_chamber_code","title","bill_type","update_date","update_date_including_text","url","latest_action_date","latest_action_text","voting_start","voting_close","schedule_date","text","advice"] 


class BillVoteSerializer(serializers.ModelSerializer):
    bill = BillSerializer()
    voter = UserSerializer()
    class Meta:
        model = billModels.BillVote
        fields = ["bill","voter","voted_by","your_vote","vote_date","last_update"]