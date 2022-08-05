import json
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from vote import models as voteModels
from api import serializers as apiSerializers 
import api.views as apiView
from django.contrib.auth.models import User

class HouseKeepingConsumer(WebsocketConsumer):
    def connect(self):
        self.pod_name = self.scope['url_route']['kwargs']['pod_name']
        self.user_name = self.scope['url_route']['kwargs']['user_name']
        self.room_group_name = 'chat_%s' % self.pod_name
        data = {}
        try:
            pod = ''
            if self.pod_name:
                pod = voteModels.Pod.objects.get(code = self.pod_name)
            # get all the pod members. 
            podMembers = pod.podmember_set.all()
            
            data = {
                "pod": apiSerializers.PodSerializer(pod).data,
                "podMembers": apiSerializers.PODMemberSer(podMembers, many=True).data
            }
        except:
            print("something went wrong...")

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
        self.send(text_data=json.dumps({
            'type':'podmember',
            'data': data
        }))
        
    def disconnect(self, close_code):
        # Leave room group
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # Send message to room group
    
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat',
                'data': switch(text_data_json)
            }
        )
     # Receive message from room group
    def chat(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type':event['data']['type'],
            'data': event['data']
        }))


def majorityVotes(pod, condidate):
    pod_members = pod.podmember_set.all()
    member_vote = condidate.podmember_vote_in_set.all()
    if member_vote.count() >= (pod_members.count()/2):
        return True
    return False

def switch(text_data_json):
    match text_data_json['type']:
        case 'podInvitationKey':
            pod = voteModels.Pod.objects.get(code = text_data_json['pod'])
            pod.invitation_code = apiView.pod_invitation_generator()
            pod.save()
            return {'type':text_data_json['type'], 'data':apiSerializers.PodSerializer(pod).data}
        case 'joined':
            pod = voteModels.Pod.objects.get(code = text_data_json['pod'])
            return {'type':text_data_json['type'], 'data':apiSerializers.PODMemberSer(pod.podmember_set.all(), many=True).data}

        case 'voteIn':
            """vote on condidate in and check if the condidate has 50+1 vote to become members.
            if so, return the podmembers. else return that the vote in has been done only.
            also check if the user already voted in for him/her
            """
            # search on vote In for condidate and the user
            user = User.objects.get(username = text_data_json['voter'])
            condidate = voteModels.PodMember.objects.get(pk = text_data_json['condidate'])
            votedIn = voteModels.PodMember_vote_in.objects.filter(condidate = condidate, voter = user).exists()
            if votedIn:
                return {
                    'type':text_data_json['type'], 
                    'done': False,
                    'voter': user.username,
                    'data':'you have already voted in for thie condidate.'
                    }

            voteIN = voteModels.PodMember_vote_in.objects.create(condidate = condidate, voter = user)
            voteIN.save()
            # check if condidate has got the majority votes
            if majorityVotes(condidate.pod, condidate):
                condidate.is_member = True
                condidate.save()
                # set the member.user.users.userType to 1 as it becomes the member in a pod.
                userType = condidate.user
                userType.users.userType = 1
                userType.save()
                podMembers = condidate.pod.podmember_set.all()
                return {
                    'type': text_data_json['type'],
                    'done': True,
                    'voter': user.username,
                    'is_member':condidate.is_member, 
                    'data':apiSerializers.PODMemberSer(podMembers, many=True).data
                    }

            return {'type': text_data_json['type'],'done':True, 'voter':user.username,'data':"voted in"}

        case 'voteOut':
            """currently there is no vote out functionality"""
            return {'type': text_data_json['type'], 'data':"voted out"}

        case 'desolvePod':
            """check if the pod has one member only and he/she is delegate. 
            in case of removing, return pod removed done else return not aligible to remove """
            pod = voteModels.Pod.objects.get(code = text_data_json['pod'])
            user = User.objects.get(username = text_data_json['user'])
            # check if the pod has only one member.
            if pod.podmember_set.all().count() <=1:
                member = pod.podmember_set.all()[0]
                if member.user == user and member.is_delegate:
                    pod.delete()
                    user.users.userType = 0
                    user.save()
                    return {'type': text_data_json['type'],'done':True, 'data':"removed the pod"}

            return {'type': text_data_json['type'],'done':False, 'data':"unable to remove"}

        case default:
            return {'type': 'notype', 'data':'no action to preferm'}