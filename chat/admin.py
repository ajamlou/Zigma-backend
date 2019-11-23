from django.contrib import admin
from .models import ChatMessage, Inbox

admin.site.register(Inbox)
admin.site.register(ChatMessage)
