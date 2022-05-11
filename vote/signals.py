from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver 
from vote import models

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        models.Users.objects.create(user = instance)
        # print("user profile createds")

@receiver(post_save, sender=User)
def save_profile(sender, instance, *args, **kwargs):
    instance.users.save()
    # print("user profile saved")