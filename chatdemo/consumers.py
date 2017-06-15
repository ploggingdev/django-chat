from channels import Group
from channels.sessions import channel_session
from .models import ChatMessage
from django.contrib.auth.models import User
import json
from channels.auth import channel_session_user, channel_session_user_from_http
from django.utils.html import escape
from django.core import serializers
import markdown
import bleach
import re
from django.conf import settings
from django.urls import reverse
from channels_presence.models import Room
from channels_presence.decorators import touch_presence

from django.dispatch import receiver
from channels_presence.signals import presence_changed
from channels import Group

@channel_session_user_from_http
def chat_connect(message):
    Group("all").add(message.reply_channel)
    Room.objects.add("all", message.reply_channel.name, message.user)
    message.reply_channel.send({"accept": True})

@touch_presence
@channel_session_user
def chat_receive(message):
    data = json.loads(message['text'])
    if not data['message']:
        return
    if not message.user.is_authenticated:
        return
    current_message = escape(data['message'])
    urlRegex = re.compile(
            u'(?isu)(\\b(?:https?://|www\\d{0,3}[.]|[a-z0-9.\\-]+[.][a-z]{2,4}/)[^\\s()<'
            u'>\\[\\]]+[^\\s`!()\\[\\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019])'
        )
    
    processed_urls = list()
    for obj in urlRegex.finditer(current_message):
        old_url = obj.group(0)
        if old_url in processed_urls:
            continue
        processed_urls.append(old_url)
        new_url = old_url
        if not old_url.startswith(('http://', 'https://')):
            new_url = 'http://' + new_url
        new_url = '<a href="' + new_url + '">' + new_url + "</a>"
        current_message = current_message.replace(old_url, new_url)
    m = ChatMessage(user=message.user, message=data['message'], message_html=current_message)
    m.save()

    my_dict = {'user' : m.user.username, 'message' : current_message}
    Group("all").send({'text': json.dumps(my_dict)})

@channel_session_user
def chat_disconnect(message):
    Group("all").discard(message.reply_channel)
    Room.objects.remove("all", message.reply_channel.name)

@receiver(presence_changed)
def broadcast_presence(sender, room, **kwargs):
    # Broadcast the new list of present users to the room.
    Group(room.channel_name).send({
        'text': json.dumps({
            'type': 'presence',
            'payload': {
                'channel_name': room.channel_name,
                'members': [user.username for user in room.get_users()],
                'lurkers': int(room.get_anonymous_count()),
            }
        })
    })

@channel_session_user_from_http
def loadhistory_connect(message):
    message.reply_channel.send({"accept": True})

@channel_session_user
def loadhistory_receive(message):
    data = json.loads(message['text'])
    chat_queryset = ChatMessage.objects.filter(id__lte=data['last_message_id']).order_by("-created")[:10]
    chat_message_count = len(chat_queryset)
    if chat_message_count > 0:
        first_message_id = chat_queryset[len(chat_queryset)-1].id
    else:
        first_message_id = -1
    previous_id = -1
    if first_message_id != -1:
        try:
            previous_id = ChatMessage.objects.filter(pk__lt=first_message_id).order_by("-pk")[:1][0].id
        except IndexError:
            previous_id = -1

    chat_messages = reversed(chat_queryset)
    cleaned_chat_messages = list()
    for item in chat_messages:
        current_message = item.message_html
        cleaned_item = {'user' : item.user.username, 'message' : current_message }
        cleaned_chat_messages.append(cleaned_item)

    my_dict = { 'messages' : cleaned_chat_messages, 'previous_id' : previous_id }
    message.reply_channel.send({'text': json.dumps(my_dict)})

@channel_session_user
def loadhistory_disconnect(message):
    pass