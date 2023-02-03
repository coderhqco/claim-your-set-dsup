from django.urls import re_path
from live import consumers, podBackNForthConsumers

websocket_urlpatterns = [
    re_path(r'ws/pod/(?P<pod_name>\w+)/(?P<user_name>\w+)/$', 
            consumers.HouseKeepingConsumer.as_asgi()
        ),
    re_path(r'ws/pod-back-n-forth/(?P<pod_name>\w+)/(?P<user_name>\w+)/$', 
            podBackNForthConsumers.PodBackNForth.as_asgi()
        ),
    re_path(r'ws/(?P<podName>\w+)/(?P<userName>\w+)',consumers.PodBackNForth.as_asgi()),
]
