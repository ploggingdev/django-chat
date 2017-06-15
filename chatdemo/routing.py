from channels.routing import route
from channels import include
from chatdemo.consumers import chat_connect, chat_disconnect, chat_receive, loadhistory_connect, loadhistory_disconnect, loadhistory_receive

chat_routing = [
    route("websocket.connect", chat_connect),
    route("websocket.receive", chat_receive),
    route("websocket.disconnect", chat_disconnect)
]

loadhistory_routing = [
    route("websocket.connect", loadhistory_connect),
    route("websocket.receive", loadhistory_receive),
    route("websocket.disconnect", loadhistory_disconnect)
]

channel_routing = [
    include(chat_routing, path=r"^/ws/$"),
    include(loadhistory_routing, path=r"^/loadhistory/$"),
]