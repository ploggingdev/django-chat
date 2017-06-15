from channels.routing import route
from channels import include
from chatdemo.consumers import chat_connect, chat_disconnect, chat_receive

chat_routing = [
    route("websocket.connect", chat_connect),
    route("websocket.receive", chat_receive),
    route("websocket.disconnect", chat_disconnect)
]

channel_routing = [
    include(chat_routing, path=r"^/ws/$"),
]