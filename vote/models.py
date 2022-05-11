from operator import truediv
from django.db import models


class Districts(models.Model):
    name = models.CharField(max_length=60, null=True, blank=True)
    code = models.CharField(max_length=4, null=True, blank=True)

    # to loaddata into district tables, run the loaddata command for fixture 
    # python loaddata <path>fileName.json
    
    class Meta:
        ordering = ['code']
        pass

    def __str__(self) -> str:
        return super().self.code


