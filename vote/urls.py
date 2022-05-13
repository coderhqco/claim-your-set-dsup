from django.urls import path
from django.views.generic import TemplateView
from vote import views as voteViews
urlpatterns = [
    path('', TemplateView.as_view(template_name='vote/index.html'), name='home'),
    path('confirm', TemplateView.as_view(template_name='vote/signUpConfirm.html'), name='test'),
    path('claim-your-seat',voteViews.ClainYourSeat, name="ClainYouSeat"),
    path('enter-the-floor',voteViews.EnterTheFloor.as_view(), name="EnterTheFloor"),
    path('activate/<uidb64>/<token>/',voteViews.activate, name='activate'),
]
