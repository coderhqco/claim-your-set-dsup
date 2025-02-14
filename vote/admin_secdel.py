from django.contrib import admin
from vote.models_secdel import SecDel

@admin.register(SecDel)
class SecDelAdmin(admin.ModelAdmin):
    list_display = ['id', 'circle', 'user', 'created_at', 'updated_at']
    list_filter = ['circle', 'user']
    search_fields = ['circle__code', 'user__username']