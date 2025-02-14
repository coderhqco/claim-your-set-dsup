import json
from django.core.mail import send_mail
import os
from rest_framework.permissions import AllowAny
from django.template.loader import render_to_string
from django.conf import settings
from curses.ascii import NUL
from rest_framework import viewsets
from vote import models as voteModels
from api import serializers as apiSerializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from vote.token import account_activation_token
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


from api import models as apiModels

class CustomPagination(PageNumberPagination):
    """
    We are creating a custome pagination
    to limit the query and more """
    page_size = 10  # Number of items per page
    # Allows the client to override the page size
    page_size_query_param = 'page_size'
    max_page_size = 100  # Maximum page size to prevent abuse


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
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        users = None
        return Response({"status": 'exception!'}, status=status.HTTP_400_BAD_REQUEST)
    if users is not None and account_activation_token.check_token(users, token):
        users.is_active = User.objects.filter(
            id=uid).update(is_active=True, is_staff=True)
        return JsonResponse({'entry_code': users.username}, safe=False)
    else:
        return Response({"status": 'Activation link is invalid!'}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = apiSerializers.PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = apiSerializers.PasswordResetRequestSerializer(
            data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            mail_subject = 'Reset your password'
            # prepare the email by template
            message = render_to_string('api/resetPasswordEmail.html', {
                'user': user,
                'domain': os.environ.get('APP_DOMAIN'),
                'protocol': 'https',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

            send_mail(
                mail_subject,
                message,
                settings.EMAIL_HOST_USER,
                [email]
            )
            return Response({"message": "Email sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = apiSerializers.PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password is reset"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        authedUser = authenticate(
            request, username=post_data['username'], password=post_data['password'])

        if authedUser is not None:
            # authenticate if has the same district code
            dist = voteModels.Districts.objects.get(
                code=post_data['district'].upper())
            if authedUser.users.district != dist:
                messages = 'Invalid Credential. Check if you have entered the right district code'
                return Response({"status": messages}, status=status.HTTP_400_BAD_REQUEST)

            # login(request,authedUser)
            data = {
                'legalName': authedUser.users.legalName,
                'username': authedUser.username,
                'email': authedUser.email,
                'userType': authedUser.users.userType,
                'address': authedUser.users.address,
                'verificationScore': authedUser.users.verificationScore,
                'is_reg': authedUser.users.is_reg,
                'district': authedUser.users.district.code,
                'date_joined': authedUser.date_joined,
            }
            return JsonResponse(data)
        else:
            messages = "Invalid Credential"
            return Response({"status": messages}, status=status.HTTP_400_BAD_REQUEST)


def circle_invitation_generator():
    """ this function is being used in cnosumerCircle as well
    this is the circle code generator.
    It uses random and checks for the database.
    return the code if it's not taken
    """
    import random
    code = str(random.randint(0, 9999999999))
    is_exist = voteModels.Group.objects.filter(invitation_code=code).exists()
    if is_exist:
        circle_invitation_generator()
    
    return code


def circle_code_generator():
    """
    this is the circle code generator.
    It uses random and checks for the database.
    return the code if it's not taken
    """

    import random
    code = str(random.randint(1, 99999))
    is_exist = voteModels.Group.objects.filter(code=code).exists()

    if is_exist:
        circle_code_generator()
    
    return code


class CreateCIRCLE(APIView):
    """
    creates a circle.
    it set the userType to 1.
    it set the user as a delegate circle member
    """

    def post(self, request):
        try:
            user = NUL
            district = NUL
           
            if 'user' in request.data and 'district' in request.data:
                user = User.objects.get(username=request.data['user'])
                district = voteModels.Districts.objects.get(
                    code=request.data['district'])
                print("user: ", user, "district: ", district)
            else:
                print("could not get the user and district: ", user, district)
                messages = "User and District are required."
                return Response({"message:": messages}, status=status.HTTP_400_BAD_REQUEST)

            # check if the userType is not 0 return
            print("got the user and district and moving to check the user type")
            if user.users.userType != 0:
                messages = "Already belongs to a circle."
                return Response({"message": messages}, status=status.HTTP_400_BAD_REQUEST)

            print("user type is zeero and checked. moving to create a circle")
            # create a circle
            code = circle_code_generator()
            invite_code = circle_invitation_generator()
            print("code: ", code, "invite_code: ", invite_code)
            circle = voteModels.Group.objects.create(
                code=code,
                district=district,
                invitation_code=invite_code,
                group_type=0,
                parent_group=None
            )
            
            print("Cirle to save: ", circle)
            
            circle.save()
            print("circle saved")
            # set the userType attribute of the creator to 1
            user.users.userType += 1
            print("user:, " , user, user.users.userType)
            # user.save()
            # print("after save: " , user, user.users.users.userType)
            user.users.save()
            # print("after save sae--: " , user.users, user.users.userType)

            # add the user to circle member as delegate
            print("circle member to save: ", user.username, circle.code,)
            circle_member_obj = voteModels.GroupMember.objects.create(
                user=user,
                group=circle,
                is_delegate=True,
                is_member=True
            )
            print("circle member to save: ", circle_member_obj)
            circle_member_obj.save()

            print("circle member saved")

            obj = apiSerializers.CircleSerializer(circle)
            print("obj: ", obj.data)

            return JsonResponse(obj.data)
        except:
            messages = "Something Went Wrong."
            return Response({"message:": messages}, status=status.HTTP_400_BAD_REQUEST)


class CircleMem(APIView):
    # check if this class is even being used...
    # It retrives all the circlemembers of all circles.
    # something we do not want
    def post(self, request):
        try:
            circle = voteModels.CircleMember.objects.all()
            return Response(apiSerializers.CIRCLEMemberSer(circle, many=True).data, status=status.HTTP_200_OK)
        except:
            return JsonResponse({False: True})


class UserView(APIView):
    def post(self, request):
        try:
            user = NUL
            print("")
            if 'user' in request.data:
                user = User.objects.get(username=request.data['user'])
            else:
                messages = "user is required."
                return Response({"message": messages}, status=status.HTTP_400_BAD_REQUEST)

            # check if the user is a member of a circle
            circle_members = voteModels.GroupMember.objects.filter(user_id=user.id).first()

            if circle_members:
                # get the circle of the user
                circle = circle_members.group

                # check if the user is a delegate
                if user.users.userType == 1:
                    return JsonResponse({
                        "circle": apiSerializers.CircleSerializer(circle).data,
                        "user": apiSerializers.UserSerializer(user).data,
                    })

            return JsonResponse({"user": apiSerializers.UserSerializer(user).data, })

        except Exception as e:
            messages = "Something Went Wrong."
            if not json.loads(os.environ.get('PRODUCTION').lower()):
                print(f'Error: {e}')
            return Response({"message": messages}, status=status.HTTP_400_BAD_REQUEST)


class HouseKeeping(APIView):
    def post(self, request):
        try:
            circle = NUL
            if 'circle' in request.data:
                circle = voteModels.Group.objects.get(code=request.data['circle'])
            else:
                messages = "CIRCLE is required."
                return Response({"message": messages}, status=status.HTTP_400_BAD_REQUEST)

            # get all the circle members.
            circleMembers = circle.circlemember_set.all()

            data = {
                "circle": apiSerializers.CircleSerializer(circle).data,
                "circleMembers": apiSerializers.CIRCLEMemberSer(circleMembers, many=True).data
            }
            return JsonResponse(data)
        except:
            messages = "Something Went Wrong."
            return Response({"message": messages}, status=status.HTTP_400_BAD_REQUEST)


def circle_joining_validation(user, circle):
    """
    this function validate weather a user can enter a circle.
    It check if circle is active.
    It check if user is already a member
    It check if userType is 0
    It checks if the user is the same districts as circle distract
    """
    result = True
    # if not circle.is_active():
    #     print("circle is active")
    #     result = False

    circlemembers = circle.groupmember_set.all()
    if circlemembers.count() >= 12:
        result = False

    if circlemembers.filter(user=user):
        result = False

    if user.users.userType > 0:
        result = False

    if user.users.district != circle.district:
        result = False

    return result


class JoinCIRCLE(APIView):
    def post(self, request):
        try:
            group = NUL
            user = NUL
            if 'circle' in request.data and 'user' in request.data:
                group = voteModels.Group.objects.get(
                    invitation_code=request.data['circle'])
                user = User.objects.get(username=request.data['user'])
            else:
                messages = "CIRCLE  and user are required."
                return Response({"message": messages}, status=status.HTTP_400_BAD_REQUEST)

            # get the circle and add the user as the member or candidate
            print("here: , ", group, user)
            if group:
                # check if user can join the circle
                if circle_joining_validation(user, group):
                    circleMember = voteModels.GroupMember.objects.create(
                        user=user,
                        group=group,
                        is_member=False,
                        is_delegate=False,
                        member_number=group.groupmember_set.count()+1
                    )
                    circleMember.save()
                    # set the userType of the member to 0
                    # when the user become the member via majority votes, then the userType is set to 1
                    circleMember.user.users.userType = 1
                    circleMember.user.users.save()
                    return JsonResponse(apiSerializers.CircleSerializer(group).data)
                else:
                    # else of circle is active
                    messages = 'either the circle is not accepting memebers or you are not eligible to join this circle'
                    return Response({"message": messages}, status=status.HTTP_400_BAD_REQUEST)

            messages = 'your request did not get processed.'
            return Response({"message": messages}, status=status.HTTP_400_BAD_REQUEST)

        except:
            messages = "Something Went Wrong."
            return Response({"message": messages}, status=status.HTTP_400_BAD_REQUEST)


def circle_desolve_check(user, circle):
    members = circle.circlemember_set.filter(is_member=True)
    if members.first().user.username != user.username:
        return False
    if not members.first().is_delegate:
        return False
    if members.count() > 1:
        return False

    return True


class DesolveCircle(APIView):
    def post(self, request):

        try:
            circle = NUL
            user = NUL
            if 'circle' in request.data and 'user' in request.data:
                circle = voteModels.Group.objects.get(code=request.data['circle'])
                user = User.objects.get(username=request.data['user'])
            else:
                messages = "Circle  and user are required."
                return Response({"message": messages}, status=status.HTTP_400_BAD_REQUEST)

            # get the circle and check weather the circle is eligible to be desolved!
            if circle:
                # check if user can join the circle
                if circle_desolve_check(user, circle):
                    circle.delete()
                    user.users.userType = 0
                    user.users.save()
                    # the user automatically sets back to userType = 0
                    return JsonResponse({"status": "desolved"})
                else:
                    # else of circle is active
                    messages = 'can not desolve the circle at the moment.'
                    return Response({"message": messages}, status=status.HTTP_400_BAD_REQUEST)
        except:
            messages = "Something Went Wrong."
            return Response({"message": messages}, status=status.HTTP_400_BAD_REQUEST)


# do we use this view ?
class CircleBackNForth(APIView):
    # list all the messsages to that Circle
    def post(self, circle):
        try:
            chats = voteModels.CircleBackNForth.objects.all()
            return Response(apiSerializers.CircleBackNForthSerializer(chats, many=True).data, status=status.HTTP_200_OK)
        except:
            return JsonResponse({False: circle})

# do we use this view as well ?


class CircleBackNForthAdd(APIView):
    # add a message to Circle Back and Forth
    def post(self, circle):
        try:
            return Response({"date": "added one message to the circle: " + circle}, status=status.HTTP_200_OK)
        except:
            return JsonResponse({False: circle})


# get the vote in for user for a circle
class CircleMemeber_voteIn(generics.ListAPIView):
    serializer_class = apiSerializers.CircleMember_VoteInSer
    queryset = voteModels.CircleMember_vote_in.objects.filter()
    permission_classes = [AllowAny]

    def get_queryset(self):
        candidate_id = self.request.query_params.get('candidate')
        if candidate_id:
            self.queryset = self.queryset.filter(voter__pk=candidate_id)
        return self.queryset

# get the vote out for user of a circle


class CircleMemeber_voteOut(generics.ListAPIView):
    serializer_class = apiSerializers.CircleMember_VoteOutSer
    queryset = voteModels.CircleMember_vote_out.objects.filter()
    permission_classes = [AllowAny]

    def get_queryset(self):
        member_id = self.request.query_params.get('member')
        if member_id:
            self.queryset = self.queryset.filter(candidate__pk=member_id)
        return self.queryset

# get the put forward for delegation of a member of a circle


class CircleMemeber_putforward(generics.ListAPIView):
    serializer_class = apiSerializers.CircleMember_put_forwardSer
    queryset = voteModels.CircleMember_put_forward.objects.filter()
    permission_classes = [AllowAny]

    def get_queryset(self):
        member_id = self.request.query_params.get('member')
        if member_id:
            self.queryset = self.queryset.filter(recipient__pk=member_id)
        return self.queryset


class CircleList(viewsets.ModelViewSet):
    serializer_class = apiSerializers.CircleSerializer
    queryset = voteModels.Group.objects.all()
    pagination_class = CustomPagination
    permission_classes = [AllowAny]


class CircleStatus(generics.ListAPIView):
    serializer_class = apiSerializers.CircleStatusSerializer
    queryset = voteModels.CircleStatus.objects.all()
    permission_classes = [AllowAny]


class TestingView(generics.ListAPIView):
    serializer_class = apiSerializers.TestingSerializer
    queryset = apiModels.TestingModel.objects.all()
    permission_classes = [AllowAny]


class UsernameRequestView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = apiSerializers.UsernameRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = apiSerializers.UsernameRequestSerializer(
            data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            mail_subject = 'Your Entry Code'

            message = render_to_string('api/usernameEmail.html', {
                'user': user,
                'domain': os.environ.get('APP_DOMAIN'),
                'protocol': 'https',
                'entry_code': user.username,
            })

            send_mail(
                mail_subject,
                message,
                settings.EMAIL_HOST_USER,
                [email]
            )
            return Response({"message": "Email sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContactInfoViewSet(viewsets.ModelViewSet):
    queryset = voteModels.ContactInfo.objects.all()
    serializer_class = apiSerializers.ContactInfoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def update(self, request, *args, **kwargs):
        user = request.user
        if not voteModels.GroupMember.objects.filter(user=user, is_delegate=True).exists():
            return Response(
                {"error": "Only delegates can modify the contact rules."},
                status = status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)