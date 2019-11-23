from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/chat/<username>/', consumers.ChatConsumer),
    path('ws/myinbox/', consumers.InboxConsumer),
]
