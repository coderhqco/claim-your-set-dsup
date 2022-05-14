from django.urls import path
from django.views.generic import TemplateView
from vote import views as voteViews

urlpatterns = [
    path('', TemplateView.as_view(template_name='vote/index.html'), name='home'),
    path('confirm', TemplateView.as_view(template_name='vote/signUpConfirm.html'), name='test'),
    path('claim-your-seat',voteViews.ClaimYourSeat, name="ClaimYourSeat"),
    path('enter-the-floor',voteViews.EnterTheFloor, name="EnterTheFloor"),
    path('activate/<uidb64>/<token>/',voteViews.activate, name='activate'),
    path('logout',voteViews.userLogout, name='logout'),
    # the home page of user
    path('home',voteViews.voterPage, name='voterPage'),

    path('pod-create',voteViews.CreatePod, name='createPod'),
    path('pod/<int:pk>/', voteViews.HouseKeepingPod.as_view(), name='pod'),

]
