from operator import mod, truediv
from pyexpat import model
from turtle import update
from django.db import models
from django.contrib.auth.models import User
# District model (table) is for listing of all US districts 
class Districts(models.Model):
    name = models.CharField(max_length=60, null=True, blank=True)
    code = models.CharField(max_length=4, null=True, blank=True)

    # to loaddata into district tables, run the loaddata command for fixture 
    # python loaddata <path>fileName.json
    
    class Meta:
        ordering = ['code']
        pass

    def __str__(self) -> str:
        return self.code


#  the django user model has the follow feilds and i only need to add to it.
# firstName, lastName,userName, email, password, isActive,
class Users(models.Model):
    # the username is districtCode + 5-digit entry code
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    legalName = models.CharField(max_length=60,null=True,blank=True)
    district = models.ForeignKey(Districts, on_delete=models.DO_NOTHING, null=True, blank=True)
    # i am registered to vote in this district
    is_reg = models.BooleanField(default=False)
    # this is for if the user is registered with conditional. 
    verificationScore = models.SmallIntegerField(default=0,null=True, blank=True)
    address = models.CharField(max_length=150, null=True, blank=True)
    # userType is the from 0 to 5. 
    userType = models.PositiveSmallIntegerField(default=0)
    voterID = models.IntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return self.user.username
    


class Pod(models.Model):
    code = models.SmallIntegerField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return super().self.code

    def is_active(self):
        # check if the member is between 6 to 12 and return true
        pass

class PodMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pod = models.ForeignKey(Pod, on_delete=models.CASCADE)
    
    # votes for others
    vote_to = models.PositiveSmallIntegerField(default=0)

    # being voted. all the votes user get
    voted = models.PositiveSmallIntegerField(default=0)
    date_joined = models.DateTimeField(auto_now_add=True)
    date_left = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_members = models.BooleanField(default=False)
    is_delegate = models.BooleanField(default=False)

    def __str__(self) -> str:
        return super().str(self.user + self.pod)
    