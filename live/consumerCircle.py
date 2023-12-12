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
        self.return_func = 0
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Fetch existing pod members using database_sync_to_async
        members = {'status':"success",'message':'listed all members.', 'member_list': await self.get_members()}
        
        # Accept the WebSocket connection
        await self.accept()

        # Send initial Circle members to the connected client
        await self.send(text_data=json.dumps(members))

    # when a member of the room leaves the room 
    async def disconnect(self, close_code):
        # Remove the client from the room (channel group)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Your custom disconnect logic here
        await self.send(text_data=json.dumps({"status": "disconnecting", "message": "Goodbye!"}))
        
        # Call the parent class disconnect method
        await super().disconnect(close_code)

    @database_sync_to_async
    def get_members(self):
        MemberInstances = voteModels.PodMember.objects.filter(pod__code=self.pod_name)
        members = serializers.PodMemberSerializer(MemberInstances, many=True)
        return members.data

    @database_sync_to_async
    def candidate_vote(self, data):
        """ Vote for candidate 
        make sure to not forget about the mejority votes to make 
        the candidate a member
        """
        try:
            voter = User.objects.get(username = data['voter'])
            candidate = voteModels.PodMember.objects.get(pk = data['candidate'])
            voteModels.PodMember_vote_in.objects.update_or_create(voter=voter, condidate=candidate)
            vote = serializers.UserSerializer(voter)
            return {"status":"success", "message":"voted successfully.", "user":vote.data}
        except:
            vote = serializers.UserSerializer(voter)
            return {"status": "error", "message": "Could not vote","user":vote.data}
    

    async def receive(self, text_data):
        """ Check messages. If message is for voting in a candidate
        then vote the candidate.
        """
        
        data = json.loads(text_data)
        
        match data["action"]:
            case "vote_in":
                # vote in the candidate and return the circle members
                self.return_func = await self.candidate_vote(data["payload"])

            case "vote_out":
                print("vote out:", data["payload"])
                # vote out the candidate and return the circle members
            case _:
                print("action not found:")
                pass

        # if any of the functions returns error, the message being sent will be that error only to that user.
        # otherwise, the circle members will be sent back to the room
        if self.return_func['status'] == 'error':
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'send_members',
                'members_list': self.return_func,
                }
            )

        else:
            await self.channel_layer.group_send(self.room_group_name, {
                    'type': 'send_members',
                    'members_list':{'status':"success", 'member_list': await self.get_members()} ,
                }
            )
            

    # Send to each member
    async def send_members(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['members_list']))
    


    