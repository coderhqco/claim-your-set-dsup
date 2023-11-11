from django.urls import re_path
from bills import billConsumer

websocket_urlpatterns = [
    re_path(r'ws/bill/$', 
        billConsumer.BillsConsumer.as_asgi()
    ),
]
