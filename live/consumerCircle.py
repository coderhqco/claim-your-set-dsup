import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async 
from channels.db import database_sync_to_async 
from django.contrib.auth.models import User
from vote import models as voteModels
from api import serializers

class CircleConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.pod_name = self.scope['url_route']['kwargs']['pod_name']
        self.user_name = self.scope['url_route']['kwargs']['user_name']
        self.room_group_name = 'chat_%s' % self.pod_name
    
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Fetch existing pod members using database_sync_to_async
        members = await self.get_members()
        
        # Accept the WebSocket connection
        await self.accept()

        # Send initial Circle members to the connected client
        await self.send(text_data=json.dumps(members))

        # when a member of the room leaves the room 
        async def disconnect(self):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            self.close()


    @database_sync_to_async
    def get_members(self):
        MemberInstances = voteModels.PodMember.objects.filter(pod__code=self.pod_name)
        members = serializers.PodMemberSerializer(MemberInstances, many=True)
        return members.data
        


    # @database_sync_to_async
    # def get_existing_vote(self, bill, username):
    #     obj = BillVote.objects.filter(bill=bill, voter__username=username).first()
    #     return obj

    # @database_sync_to_async
    # def update_existing_vote(self, existing_vote, vote_type):
    #     existing_vote.your_vote = vote_type
    #     existing_vote.save()

    # @database_sync_to_async
    # def create_new_vote(self, bill, user, vote_type):
    #     ob = BillVote.objects.create(bill=bill, voter=user, your_vote=vote_type)
    #     ob.save()
    
    # @database_sync_to_async
    # def get_user_instance(self, username):
    #     try:
    #         u_obj = User.objects.get(username = username)
    #         district_code = u_obj.users.district
    #         return u_obj, district_code
    #     except User.DoesNotExist:
    #         return None, None
        
    async def receive(self, text_data):
        data = json.loads(text_data)
        vote_type = data['vote_type']
        username = data['username']

        # Fetch existing votes for the bill using database_sync_to_async
        # try:
        #     bill = await database_sync_to_async(Bill.objects.get)(number=self.bill_id)
        # except Bill.DoesNotExist:
        #     return

        # get user instance 
        # u, district_code = await self.get_user_instance(username)
        # Check if the user has already voted for this bill
        # existing_vote = await self.get_existing_vote(bill, username)

        # if existing_vote:
        #     # Update the existing vote using database_sync_to_async
        #     await self.update_existing_vote(existing_vote, vote_type)
        # else:
        #     # Create a new vote using database_sync_to_async
        #     await self.create_new_vote(bill, u, vote_type)

        # Fetch updated votes for the bill using database_sync_to_async
        # updated_bill_votes = await self.get_bill_votes(district_code)
        # Send updated vote counts to the room group

        await self.channel_layer.group_send(self.room_group_name, {
                'type': 'update_vote_counts',
                'votes': "updated_bill_votes",
            }
        )

    # Send to each member
    async def update_vote_counts(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['votes']))
    


    