from rest_framework import viewsets
from api import models as apiModels
from api import sec_del_ser as apiSerializer
from django.contrib.auth.models import User
from vote.models import Districts
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse


class SecDelViewSet(viewsets.ModelViewSet):
    queryset = apiModels.SecDelModel.objects.all()
    serializer_class = apiSerializer.SecDelSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            user=None, 
            district =None
            if 'user' in request.data and 'district' in request.data:
                user = User.objects.get(username=request.data['user'])
                district = Districts.objects.get(
                    code=request.data['district'])
            else:
                messages = "District are required."
                return Response({"message:": messages}, status=status.HTTP_400_BAD_REQUEST)

            # check if the userType is not 0 return
            if user.users.userType != 1:
                messages = "Already belongs to a sec del."
                return Response({"message": messages}, status=status.HTTP_400_BAD_REQUEST)
            
            # create a circle
            sec_del = apiModels.SecDelModel.objects.create( district=district  )
    
            # set the userType attribute of the creator to 1
            # add the user to circle member as delegate. it does not require to save. create automatically saves as well
            apiModels.SecDelMembers.objects.create(user=user,sec_del=sec_del, is_member=True)

            obj = apiSerializer.SecDelSerializer(sec_del)
    
            return JsonResponse(obj.data)
        except:
            messages = "Something Went Wrong."
            return Response({"message:": messages}, status=status.HTTP_400_BAD_REQUEST)
        



class SecDelMembersViewSet(viewsets.ModelViewSet):
    queryset = apiModels.SecDelMembers.objects.all()
    serializer_class = apiSerializer.SecDelMembersSerializer