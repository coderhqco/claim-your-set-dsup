from dataclasses import fields
from rest_framework import serializers
from vote.models import Districts
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from vote.token import account_activation_token
from django.core.mail import EmailMessage

from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from vote import models as voteModels

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
        user.users.legalName = validated_data['legalName']
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
        current_site = get_current_site(self.context['request'])
        mail_subject = 'Activate your account.'
        message = render_to_string('api/accountActiveEmail.html', {
            'user': user,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        })
        to_email = user.email
        email = EmailMessage( mail_subject,  message,  to=[to_email] )
        email.send()

        return user

class Userializer(serializers.ModelSerializer):
    class Meta:
        model = voteModels.Users
        fields = ["legalName", "district", "is_reg","verificationScore","address","userType","voterID"]

class UserSerializer(serializers.HyperlinkedModelSerializer):
    users = Userializer()
    class Meta:
        model  = User
        fields = ["username","email","is_staff","is_active","is_superuser","users"]
        depth  = 1

class PODMemberSer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model  = voteModels.PodMember
        fields =["is_delegate","member_number","id","pod","user","is_member"]
        depth  = 3

class VoterPageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model  = voteModels.Users
        fields = "__all__"
        depth  = 1

class PodMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model  = voteModels.PodMember
        fields = "__all__"

class PodSerializer(serializers.ModelSerializer):
    district = DistrictsSerializer()
    class Meta:
        model  = voteModels.Pod
        fields = "__all__"