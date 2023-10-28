from rest_framework import routers
from django.urls import path, include

from api import views as apiViews
# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register('districts', apiViews.DistrictsViewSet)
router.register('user', apiViews.UserPageView)
router.register('voter-page', apiViews.VoterPageView)

from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', apiViews.RegisterView.as_view(), name='auth_register'),
    path('activate/<uidb64>/<token>/',apiViews.activate, name='activate'),
    path('login/', apiViews.LoginPageView.as_view()),
    path('create-pod/', apiViews.CreatePOD.as_view()),
    path('house-keeping/', apiViews.HouseKeeping.as_view()),
    path('join-pod/', apiViews.JoinPOD.as_view()),
    path('userinfo/', apiViews.UserView.as_view()),
    path('pod-desolve/', apiViews.DesolvePod.as_view()),
    path('podmember/', apiViews.PodMem.as_view()),
    
    # these urls are also associated with view that we might not use.
    path('backnforth/<pod>/', apiViews.PodBackNForth.as_view()),
    path('backnforth/<pod>/add', apiViews.PodBackNForthAdd.as_view()),
    path('create-handle/', apiViews.PodBackNForthHandle.as_view()),
]
