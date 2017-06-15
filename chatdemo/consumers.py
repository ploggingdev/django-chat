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