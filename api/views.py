from rest_framework import viewsets
from vote import models as voteModels
from api import serializers as apiSerializers
# from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django.contrib.auth.models import User
from api.serializers import RegisterSerializer
from rest_framework import generics

from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from vote.token import account_activation_token
from django.http import JsonResponse


class DistrictsViewSet(viewsets.ModelViewSet):
    queryset = voteModels.Districts.objects.all()
    serializer_class = apiSerializers.DistrictsSerializer
    
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    # permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


def activate(request, uidb64, token):
    """after the claiming your seat, this function handles the activation of user via email"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        users = User.objects.get(id=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        users = None
    if users is not None and account_activation_token.check_token(users, token):
        users.is_active = User.objects.filter(id=uid).update(is_active=True, is_staff= True)
        
        return JsonResponse({'entry_code':users.username},safe=False)
    else:
        return JsonResponse({'error':'Activation link is invalid!'},safe=False)


class UserPageView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = apiSerializers.UserSerializer

class VoterPageView(viewsets.ModelViewSet):
    queryset = voteModels.Users.objects.all()
    serializer_class = apiSerializers.VoterPageSerializer
