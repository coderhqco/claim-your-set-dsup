from django.db.models.signals import post_save, pre_save
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


# @receiver(pre_save, sender=User)
# def give_default_username(sender, instance, *args, **kwargs):
#     print("pre signal", instance.username)
#     instance.username = 'default'
#     print("pre signal", instance.username)