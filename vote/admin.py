from django.contrib import admin
from vote import models

admin.site.register(models.Districts)
admin.site.register(models.Users)
admin.site.register(models.Pod)
admin.site.register(models.PodMember)