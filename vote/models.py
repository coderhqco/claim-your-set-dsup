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

    def __str__(self):
        return str(self.code)


#  the django user model has the follow feilds and i only need to add to it.
# firstName, lastName,userName, email, password, isActive,
class Users(models.Model):
    # the username is districtCode + 5-digit entry code
    user        = models.OneToOneField(User, on_delete=models.CASCADE)
    legalName   = models.CharField(max_length=60,null=True,blank=True)
    district    = models.ForeignKey(Districts, on_delete=models.DO_NOTHING, null=True, blank=True)
    # i am registered to vote in this district
    is_reg      = models.BooleanField(default=False)
    # this is for if the user is registered with conditional. 
    verificationScore = models.SmallIntegerField(default=0,null=True, blank=True)
    address     = models.CharField(max_length=150, null=True, blank=True)
    # userType is the from 0 to 5. 
    userType    = models.PositiveSmallIntegerField(default=0)
    voterID     = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.user.username)
    
import random
class Pod(models.Model):
    code            = models.CharField(max_length=5, unique=True)
    district        = models.ForeignKey(Districts, on_delete=models.CASCADE)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    invitation_code = models.CharField(max_length=10)
    FDel_election   =  models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.code)
        
    @property
    def is_active(self):
        # check if the member <= 12 and return true
        if 6 <= self.podmember_set.filter(is_member = True).count() <= 12:
            return True
        return False

class PodMember(models.Model):
    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    pod     = models.ForeignKey(Pod, on_delete=models.CASCADE)
    date_joined     = models.DateTimeField(auto_now_add=True)
    date_updated    = models.DateTimeField(auto_now=True)
    is_member       = models.BooleanField(default=False)
    is_delegate     = models.BooleanField(default=False)
    member_number   = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.user.username)

    class Meta:
        ordering = ['-is_delegate', 'date_joined']

class PodMember_vote_in(models.Model):
    condidate   = models.ForeignKey(PodMember,related_name='voteIns', on_delete=models.CASCADE) #
    voter       = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.voter) + '-'+ str(self.condidate)

class PodMember_vote_out(models.Model):
    condidate   = models.ForeignKey(PodMember, related_name='voteOuts', on_delete=models.CASCADE)
    voter       = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.voter) + '-'+str(self.condidate)

class PodMember_put_farward(models.Model):
    recipient   = models.ForeignKey(PodMember,related_name='putFarward', on_delete=models.CASCADE) # recipient 
    voter       = models.ForeignKey(User, on_delete=models.CASCADE)  # 

    def __str__(self):
        return str(self.voter) + '-'+str(self.recipient)


# pod Back and Forth (chat) model
# sender
# Pod
# date
# message

class PodBackNForth(models.Model):
    pod = models.ForeignKey(Pod, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_created=True, auto_now_add=True)
    message = models.TextField(max_length=5000)

    def __str__(self) -> str:
        return str(self.sender.username) + " - " + str(self.pod.code)

