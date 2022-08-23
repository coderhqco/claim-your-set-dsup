import json
from os import pread
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


def majorityputFarward(recipient):
    if recipient.putFarward.all().count() >= (recipient.pod.podmember_set.all().count()/2):
        return True
    return False

def majorityVotes(condidate):
    if condidate.voteIns.all().count() >= (condidate.pod.podmember_set.all().count()/2):
        return True
    return False

def majorityVotesOut(member):
    if member.voteOuts.all().count() >= (member.pod.podmember_set.all().count()/2):
        return True
    return False

def switch(text_data_json):
    match text_data_json['type']:
        case 'podInvitationKey':
            pod = voteModels.Pod.objects.get(code = text_data_json['pod'])
            pod.invitation_code = apiView.pod_invitation_generator()
            pod.save()
            print("pod ser: ", apiSerializers.PodSerializer(pod).data)
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
                    'condidate': condidate.user.username,
                    'data':'you have already voted in for thie condidate.'
                    }

            voteIN = voteModels.PodMember_vote_in.objects.create(condidate = condidate, voter = user)
            voteIN.save()
            # check if condidate has got the majority votes
            if majorityVotes(condidate):
                condidate.is_member = True
                condidate.save()
                # set the member.user.users.userType to 1 as it becomes the member in a pod.
                userType = condidate.user
                userType.users.userType = 1
                userType.save()
                # remove all votes in for this members
                votedIn = voteModels.PodMember_vote_in.objects.filter(condidate = condidate).delete()
                podMembers = condidate.pod.podmember_set.all()
                data = {
                    'pod':apiSerializers.PodSerializer(condidate.pod).data,
                    'podmembers':apiSerializers.PODMemberSer(podMembers, many=True).data
                }
                return {
                    'type': text_data_json['type'],
                    'done': True,
                    'voter': user.username,
                    'condidate': condidate.user.username,
                    'is_member':condidate.is_member, 
                    'data':data
                    }
            return {
                'type': text_data_json['type'],
                'done':True,
                'condidate': condidate.user.username, 
                'voter':user.username,
                'data':apiSerializers.PODMemberSer(condidate.pod.podmember_set.all(), many=True).data
                }

        case 'voteOut':
            """this is for voting out a member while the pod is active"""
            user = User.objects.get(username = text_data_json['voter'])
            member =voteModels.PodMember.objects.get(pk = text_data_json['member'])
            # check if the voter is already in the vote out:
            votedOut = voteModels.PodMember_vote_out.objects.filter(voter = user, condidate = member).exists()
            if votedOut:
                return {
                    'type':text_data_json['type'], 
                    'done': False,
                    'voter': user.username,
                    'condidate': member.user.username,
                    'data':'you have already voted out for this member.'
                    }

            voteOut = voteModels.PodMember_vote_out.objects.create(condidate = member, voter = user)
            voteOut.save()
            podMembers = member.pod.podmember_set.all()
            return {
                'type': text_data_json['type'],
                'done': True,
                'voter': user.username,
                'member': member.user.username,
                'data':apiSerializers.PODMemberSer(podMembers, many=True).data
                }

        case 'delegate':
            """this functionality choose for delegation"""
            #  pod: the pod id coming from client
            # F_delFor: the person chosen as delegate
            # voter: the member who voted
            user = User.objects.get(username = text_data_json['voter'])
            recipient = voteModels.PodMember.objects.get(pk = text_data_json['recipient'])
            delegated = voteModels.PodMember_put_farward.objects.filter(voter = user, recipient = recipient).exists()
            if delegated:
                return {
                    'type':text_data_json['type'], 
                    'done': False,
                    'voter': user.username,
                    'recipient': recipient.user.username,
                    'data':'you have already delegated for this member.'
                    }
            putFrwd = voteModels.PodMember_put_farward.objects.create(recipient = recipient, voter = user)
            putFrwd.save()
            if majorityputFarward(recipient):
                # revoke the prev delegate to member
                prevDel = recipient.pod.podmember_set.get(is_delegate = True)

                recipient.is_delegate = True
                recipient.save()

                prevDel.is_delegate = False
                prevDel.save()
                # remove all the pufarward votes of prevDel
                recipient.putFarward.all().delete()

                return {
                    'type': text_data_json['type'],
                    'done': True,
                    'voter': user.username,
                    'recipient': recipient.user.username,
                    'is_delegate':recipient.is_delegate, 
                    'data':apiSerializers.PODMemberSer(recipient.pod.podmember_set.all(), many=True).data
                    }

            return {
                'type': text_data_json['type'],
                'done': True,
                'voter': user.username,
                'recipient': recipient.user.username,
                'is_delegate':recipient.is_delegate,
                'data':apiSerializers.PODMemberSer(recipient.pod.podmember_set.all(), many=True).data
                }
            

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

        case 'removemember':
            """ this case removes the condidate or member"""
            pod = voteModels.Pod.objects.get(code = text_data_json['pod'])
            member = voteModels.PodMember.objects.get(pk = text_data_json['member'])
            member.delete()
            # set the userType back to zero
            member.user.users.userType = 0
            member.user.users.save()
            data = {
                "pod": apiSerializers.PodSerializer(pod).data,
                "podMembers": apiSerializers.PODMemberSer(pod.podmember_set.all(), many=True).data
            }
            return {
                'type':text_data_json['type'], 
                'done': member.user.username,
                'data':data
                }

        case default:
            return {'type': 'notype', 'data':'no action to preferm'}