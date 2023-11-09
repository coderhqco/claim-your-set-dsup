import json
from os import pread
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer
from asgiref.sync import sync_to_async
from asgiref.sync import async_to_sync
from vote import models as voteModels
from bills import models as billModels
from api import serializers as apiSerializers
from bills import serializers as billSerializers
import api.views as apiView
from django.contrib.auth.models import User
from api.serializers import UserSerializer
from asyncio import wait_for
from django.core import serializers
from django.forms.models import model_to_dict
import asyncio
from django.core.paginator import Paginator

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
        raise StopConsumer()

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


class PodBackNForth(AsyncWebsocketConsumer):
    async def connect(self):
        # get pod and username
        self.podName = self.scope['url_route']['kwargs']['podName']
        self.userName = self.scope['url_route']['kwargs']['userName']

        # create room with podname
        self.room_group_name = self.podName
        self.username = self.userName
        self.request = self.scope.get('request')
        self.pageNum = 1
        self.paginator = 10

        # construct B&F entries 
        self.queryset_init = None

        # connect to db and retraive old messages of that pod
        self.usrs = await database_sync_to_async(self.get_messages)()
        
   
        # add user to pod room
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # send message to that web socket request only. not to the group members
        await self.send(text_data=json.dumps(self.usrs))


    def get_messages(self):
        """ Get the B&f entries and paginate them in 10 entries per page. 
        The entries are sorted from the latest to the oldest.
        """
        pod = voteModels.Pod.objects.get(code = self.podName)
        if pod:
            objects = apiSerializers.PodBackNForthSerializer(
                voteModels.PodBackNForth.objects.filter(pod=pod).order_by('-date'), many=True
                ).data
            self.queryset_init = objects

            paginator = Paginator(objects, self.paginator)  # Paginate queryset with 5 items per page
            page = paginator.get_page(self.pageNum)
            return list(page)
        return 0

    # Receive message from WebSocket
    async def receive(self, text_data):
        """Check if the page_number is in the message. 
        If so, it means to load more messages. Else, forward the new entry to the room
        """
        if "page_number" in text_data:
            page_number = text_data.split(",")[1]
            # here send the next page of the paginated queryset
            # send only to that user
            self.pageNum = page_number
            paginator = Paginator(self.queryset_init, self.paginator)  # Paginate queryset with 5 items per page
            page = paginator.get_page(self.pageNum)
            
            items = list(page)
            await self.send(text_data=json.dumps(items))
        else:
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "podChat", "message": text_data}
            )

    # handling function for sending all the messages to room members
    async def podChat(self, event):
        # save the incoming messages into DB here.
        self.usrs = await database_sync_to_async(self.save_message)(event['message'])
        # # retrive that message and send to the front
        # message = await database_sync_to_async(self.get_message)()
        # this python manual dict is to construct an alternative response. 

        # construct a message object
        obj = {
            "id":       self.usrs.id,
            "date":     self.usrs.date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "message":  self.usrs.message,
            "pod":      self.usrs.pod.id,
            "sender":   self.usrs.sender.username,
        }
        await self.send(text_data=json.dumps(obj))

    # when a member of the room leaves the room 
    async def disconnect(self,message):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        self.close()
    #  get the last message instance when user send a message
   
    def get_message(self):
        # get the last message instance when a member sends a message and to send it back.
        pod = voteModels.Pod.objects.first()
        objects = apiSerializers.PodBackNForthSerializer(
            voteModels.PodBackNForth.objects.filter(pod=pod).filter(
                sender__username = self.userName).last()
                ).data
        return objects

    
    # get all the messages, once a user join
  
    def save_message(self,msg):
        # get pod and user instance
        pod = voteModels.Pod.objects.get(code = self.podName)
        usr = User.objects.get(username = self.userName)
        # here validate if the user is a member of the pod and create a message instance to save into DB
        objects = voteModels.PodBackNForth.objects.create( pod = pod, sender= usr, message = ""+msg,)
        objects.save()
        return objects




class VoteTallyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # get username
        self.userName = self.scope['url_route']['kwargs']['userName']

        # initialize variables
        self.poll_group_name = 'vote_tally'
        self.username = self.userName
        self.userObj = User.objects.get(username=self.username)
        self.district_code = self.userObj.users.district
        self.request = self.scope.get('request')

        await self.channel_layer.group_add(
            self.poll_group_name,
            self.channel_name
        )
        await self.accept()

        self.tallies = []
        # connect to db and retrieve bill tallies
        async for bill in billModels.Bill.objects.all().order_by('-number'):
            tally = await self.get_tally(bill)
            self.tallies.append(tally) 
        # add user to room
        await self.channel_layer.group_add(self.poll_group_name, self.channel_name)
        await self.accept()
        # send tallies to that web socket request only. not to the group members
        await self.send(text_data=json.dumps(self.tallies))


    # Receive message from WebSocket
    async def receive(self, text_data):
        await self.channel_layer.group_send(
            self.poll_group_name, {"type": "billLive", "message": text_data}
        )


    # handling function for sending all the bills to room members
    async def billLive(self, event):
        # save the updated bills into DB here.
        self.tallies = await self.update_vote(event['message']['number'],event['message']['choice'])
        await self.send(text_data=json.dumps(self.tallies))


    # when a member of the room leaves the room 
    async def disconnect(self,message):
        await self.channel_layer.group_discard(self.poll_group_name, self.channel_name)
        self.close()
    
    
    async def update_vote(self,bill_number,vote_choice):
        BillObj = billModels.Bill.get(number=bill_number)      
        billModels.BillVote.filter(bill__number=bill_number,voter__username=self.userName).update(your_vote=vote_choice)
        t = await self.get_tally(BillObj)
        return list(t)


    async def get_tally(self,bill):
        bill_num = bill.number
        Yea = await database_sync_to_async(bill.count_yea_votes)()
        Nay = await database_sync_to_async(bill.count_nay_votes)()
        Pr = await database_sync_to_async(bill.count_present_votes)()
        Px = await database_sync_to_async(bill.count_proxy_votes)()

        return {"number":bill_number,"Y":Yea,"N":Nay,"Pr":Pr,"Px":Px}





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
            return {'type':text_data_json['type'], 'data':apiSerializers.PodSerializer(pod).data}
        case 'joined':
            pod = voteModels.Pod.objects.get(code = text_data_json['pod'])
            return {'type':text_data_json['type'], 'data':apiSerializers.PODMemberSer(pod.podmember_set.all(), many=True).data}

        case 'voteIn':
            """vote a condidate in and check if the condidate has 50+1 vote to become members or circle.
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

                
                # here you have to update the FDel field of the pod as true 
                # indicating that the pod had it's first election 

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