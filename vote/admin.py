from django.contrib import admin
from vote import models

admin.site.register(models.Districts)


admin.site.register(models.Users)

admin.site.register(models.Pod)
admin.site.register(models.PodMember)
admin.site.register(models.PodMember_vote_in)
admin.site.register(models.PodMember_vote_out)
admin.site.register(models.PodMember_put_farward)

admin.site.register(models.PodBackNForth)