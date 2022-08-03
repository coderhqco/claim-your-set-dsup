from django.urls import re_path
from live import consumers

websocket_urlpatterns = [
    re_path(r'ws/pod/(?P<pod_name>\w+)/(?P<user_name>\w+)/$', consumers.LivConsumer.as_asgi())
]
