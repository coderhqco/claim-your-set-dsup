from rest_framework import routers
from django.urls import path, include

from api import views as apiViews
# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register('districts', apiViews.DistrictsViewSet)

urlpatterns = [
    path('', include(router.urls))
]
