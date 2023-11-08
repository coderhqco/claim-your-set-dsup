from rest_framework import routers
from django.urls import path, include
from bills import views as billViews
from bills.views import get_bills

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('bills/', get_bills, name='get_bills'),
    path('update_bill/', billViews.BillUpdate.as_view()),
    path('<int:number>/delete_bill/', billViews.BillDelete.as_view()),
    
]