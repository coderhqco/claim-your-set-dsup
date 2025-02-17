from rest_framework import viewsets
from api import models as apiModels
from api import sec_del_ser as apiSerializer


class SecDelViewSet(viewsets.ModelViewSet):
    queryset = apiModels.SecDelModel.objects.all()
    serializer_class = apiSerializer.SecDelSerializer


class SecDelMembersViewSet(viewsets.ModelViewSet):
    queryset = apiModels.SecDelMembers.objects.all()
    serializer_class = apiSerializer.SecDelMembersSerializer