from rest_framework import viewsets
from vote import models as voteModels
from api import serializers as apiSerializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from vote.token import account_activation_token
from django.http import JsonResponse
from django.contrib.auth import authenticate,login


class DistrictsViewSet(viewsets.ModelViewSet):
    queryset = voteModels.Districts.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = apiSerializers.DistrictsSerializer
    
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = apiSerializers.RegisterSerializer


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


class LoginPageView(APIView):
    """
    View to list all users in the system.
    * Requires token authentication.
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        """
        authenticate user and return the use object to the voterpage
        """
        post_data = request.data
        # username is the entry-code
        authedUser = authenticate(request, username=post_data['username'], password=post_data['password'])

        if authedUser is not None:
            # authenticate if has the same district code
            dist = voteModels.Districts.objects.get(code = post_data['district'].upper())
            if authedUser.users.district != dist:
                messages = 'Invalid Credential. Check if you have entered the right district code'
                return Response({"status":messages}, status=status.HTTP_400_BAD_REQUEST)

            # login(request,authedUser)
            data ={
                'legalName': authedUser.users.legalName,
                'username': authedUser.username,
                'email' : authedUser.email,
                'userType': authedUser.users.userType,
                'address': authedUser.users.address, 
                'verificationScore': authedUser.users.verificationScore, 
                'is_reg':authedUser.users.is_reg, 
                'district': authedUser.users.district.code,
            }
            return JsonResponse(data)
        else:
            messages="Invalid Credential"
            return Response({"status":messages}, status=status.HTTP_400_BAD_REQUEST)