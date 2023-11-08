from django.contrib import admin

# Register your models here.
import bills.models as models
admin.site.register(models.Bill)
admin.site.register(models.BillVote)