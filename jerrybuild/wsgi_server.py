"""
Multithreaded WSGI-compatible server for bottle.
"""

import sys
from wsgiref.simple_server import make_server, WSGIServer
if sys.version_info.major > 2:
    from socketserver import ThreadingMixIn
else:
    from SocketServer import ThreadingMixIn


class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    daemon_threads = True


class WSGIServer:
    def __init__(self, wsgi_app, listen='127.0.0.1', port=8080):
        self.wsgi_app = wsgi_app
        self.listen = listen
        self.port = port
        self.server = make_server(self.listen, self.port, self.wsgi_app,
                                  ThreadingWSGIServer)

    def serve_forever(self):
        self.server.serve_forever()
