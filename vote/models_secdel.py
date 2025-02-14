from django.db import models
from django.contrib.auth.models import User
from vote.models import Group
   
# Sec-Del model that stores secondary delagate info
class SecDel(models.Model):
    id = models.PositiveIntegerField(primary_key=True, unique=True, auto_created=True, editable=False)
    circle = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="sec_dels")                        #Circle association
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sec_dels")                           #User assigned as Sec-Del
    created_at = models.DateTimeField(auto_now_add=True)                                                        #Timestamp for creation
    updated_at = models.DateTimeField(auto_now=True)                                                            #->for updates

    def save(self, *args, **kwargs):
        if not self.id:
            #unique 4-digit ID for SecDel
            self.id = SecDel.objects.aggregate(max_id=models.Max('id'))['max_id']
            self.id = (self.id or 999) + 1                                                                      #start from 1000 if no records exist
        super(SecDel, self).save(*args, **kwargs)

    def __str__(self):
        return f"SecDel {self.id}: {self.user.username} ({self.circle.code})"
