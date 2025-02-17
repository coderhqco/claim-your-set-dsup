import random
from django.db import models
from vote.models import Districts
from django.contrib.auth.models import User

def generate_unique_code():
    while True:
        code = random.randint(1000, 9999)
        if not SecDelModel.objects.filter(code=code).exists():
            return code

def generate_unique_invitation_key():
    while True:
        invitation_key = random.randint(1000000000, 9999999999)
        if not SecDelModel.objects.filter(invitation_key=invitation_key).exists():
            return invitation_key


class SecDelModel(models.Model):
    code = models.PositiveIntegerField(unique=True, default=generate_unique_code)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    district = models.ForeignKey(Districts, on_delete=models.CASCADE)
    invitation_key = models.PositiveBigIntegerField(unique=True, default=generate_unique_invitation_key)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_code()
        if not self.invitation_key:
            self.invitation_key = generate_unique_invitation_key()
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        # check if the member <= 12 and return true
        if 6 <= self.secdelmembers_set.filter(is_member = True).count() <= 12:
            return True
        return False



# the user can be changed to be Circle delegate only. but being a user is much better
class SecDelMembers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sec_del = models.ForeignKey(SecDelModel, on_delete=models.CASCADE)
    is_delegate = models.BooleanField(default=False)
    is_member = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_delegate', 'joined_at']
    
