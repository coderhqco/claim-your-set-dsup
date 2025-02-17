from django.contrib import admin
from api import models as apiModels


class SecDel_Admin(admin.ModelAdmin):
    list_display =['code','invitation_key', 'district','created_at']
    list_display_links =['code','invitation_key', 'district','created_at']
    search_fields =['code','invitation_key','district','created_at']

admin.site.register(apiModels.SecDelModel, SecDel_Admin)