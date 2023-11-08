from rest_framework import serializers
from vote.models import Districts
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_encode
from vote.token import account_activation_token
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from vote import models as voteModels
from bills import models as billModels
import os


class DistrictsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Districts
        fields = [ 'name', 'code']
    
def entry_code_generator():
    """
    this is the entry code generator. 
    It uses random and checks for the database. 
    return the code if it's not taken
    """
    import random
    code  = str(random.choice('abcdefghijklmnpqrstuvwxyz'))
    code += str(random.randint(1,9))
    code += str(random.choice('abcdefghijklmnpqrstuvwxyz'))
    code += str(random.randint(1,9))
    code += str(random.choice('abcdefghijklmnpqrstuvwxyz'))
    code = code.upper()
    is_exist = User.objects.filter(username = code).exists()

    if is_exist:
        entry_code_generator()
    return code

class RegisterSerializer(serializers.ModelSerializer):
    email       = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password    = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2   = serializers.CharField(write_only=True, required=True)
    district    = serializers.CharField(write_only=True)
    legalName   = serializers.CharField(write_only=True)
    is_reg      = serializers.BooleanField(required=False)
    is_reg1     = serializers.BooleanField(required=False)
    address     = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 
                'district', 'legalName', 'is_reg', 'is_reg1', 'address')
        # extra_kwargs = {
        #     'first_name': {'required': True},
        #     'last_name': {'required': True}
        # }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=entry_code_generator(),
            email=validated_data['email'],
            is_active = False,
            # first_name=validated_data['first_name'],
            # last_name=validated_data['last_name']
        )
        
        user.set_password(validated_data['password'])
        user.save()
        # set the user profile instance
        user.users.legalName = validated_data['legalName'].upper()
        
        user.users.address=validated_data['address']

        # add user district
        from vote.models import Districts
        dist = Districts.objects.filter(code = validated_data['district'].upper()).first()
        if not dist:
            raise serializers.ValidationError({"district": "district didn't match."})

        user.users.district = dist

        # set if user should be notified within 30 days
        if validated_data['is_reg1']:
            user.users.is_reg = True

        user.save()
        # send email and get url and encode 
        mail_subject = 'Activate your account.'
        message = render_to_string('api/accountActiveEmail.html', {
            'user': user,
            'domain': os.environ.get('APP_DOMAIN'),
            'protocol': 'https' if self.context['request'].is_secure() else 'http',
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        })
        send_mail( mail_subject, message, settings.EMAIL_HOST_USER, [user.email] )
        return user

class Userializer(serializers.ModelSerializer):
    district = DistrictsSerializer()
    class Meta:
        model = voteModels.Users
        fields = ["legalName", "district", "is_reg","verificationScore","address","userType","voterID"]

class UserSerializer(serializers.HyperlinkedModelSerializer):
    users = Userializer()
    class Meta:
        model  = User
        fields = ["username","email","is_staff","is_active","users","date_joined"]
        depth  = 1

class PodSerializer(serializers.ModelSerializer):
    district = DistrictsSerializer()
    # is_active is a property defined on the model
    is_active = serializers.ReadOnlyField()
    class Meta:
        model  = voteModels.Pod
        fields = "__all__"

class PodMember_VoteInSer(serializers.ModelSerializer):
    class Meta:
        model = voteModels.PodMember_vote_in
        fields = '__all__'

class PodMember_VoteOutSer(serializers.ModelSerializer):
    class Meta:
        model = voteModels.PodMember_vote_out
        fields = '__all__'

class PODMemberSer(serializers.ModelSerializer):
    user = UserSerializer()
    pod = PodSerializer()
    voteIns = serializers.StringRelatedField(many=True)
    voteOuts = serializers.StringRelatedField(many=True)
    putFarward = serializers.StringRelatedField(many=True)

    class Meta:
        model  = voteModels.PodMember
        fields =["is_delegate","member_number","id",'user','pod',"is_member", 'voteIns','voteOuts','putFarward']
        

class VoterPageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model  = voteModels.Users
        fields = "__all__"
        depth  = 1


class PodBackNForthSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    class Meta:
        model   = voteModels.PodBackNForth
        fields  = ["id", "sender","message", "pod", 'date']


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