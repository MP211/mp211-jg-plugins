import gremlin
from gremlin.user_plugin import *

import threading
import socket
from urllib.parse import urlparse
#import urllib.request


mode = ModeVariable(
    "Mode",
    "The mode to use for this mapping"
)
btn = PhysicalInputVariable(
    "Button",
    "Button which will trigger the GET request to URI.",
    [gremlin.common.InputType.JoystickButton]
)
uri = StringVariable(
    "URI",
    "URI for GET request.",
    "http://"
)


decorator_b = btn.create_decorator(mode.value)

request_thread = None

def http_get():
    uri_parts   = urlparse(uri.value)
    uri_addr    = uri_parts.netloc.split(':')
    host        = uri_addr[0]
    port        = uri_addr[1] if len(uri_addr) > 1 else 80
    # if host == 'localhost':
    #     host = '127.0.0.1'
    conn_host   = (host, port)

    payload = "GET %s HTTP/1.1\r\n" % ( uri_parts.path or '/' )
    payload += "Host: %s:%s\r\n" % conn_host
    payload += "Connection: close\r\n"
    payload += "\r\n"
    gremlin.util.log(payload)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect( conn_host )
    try:
        client.sendall( payload.encode() )
    except socket.error as e:
        gremlin.util.log(e)

    data = b''
    while True:
        buf = client.recv(4096)
        if not buf:
            break
        data += buf
    client.shutdown(1)
    client.close()
    gremlin.util.log("RECV {}".format( repr(data.decode()) ) )

    # is this necessary?
    threading.current_thread().join()


@decorator_b.button(btn.input_id)
def button_e(event, vjoy):
    global request_thread
    if event.is_pressed:
        if request_thread is None or request_thread.is_alive() is False:
            request_thread = threading.Thread(target=http_get)
            request_thread.start()

