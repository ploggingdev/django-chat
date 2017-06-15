from django.contrib import admin

from .models import ChatMessage

from .forms import AdminChatMessageForm

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    form = AdminChatMessageForm
    list_display = ('user','message','updated','created')