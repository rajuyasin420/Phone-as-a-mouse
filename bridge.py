"""
bridge.py — serves the gyro web page to the phone over HTTPS,
and forwards every motion packet it receives to my_mouse.py via UDP.

phone Safari --HTTPS--> this bridge --UDP--> my_mouse.py (port 9999, unchanged)
"""
import http.server
import ssl
import socket
import os

HERE = os.path.dirname(os.path.abspath(__file__))

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # sender socket — ONCE

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # any GET -> hand the phone the web page
        with open(os.path.join(HERE, "index.html"), "rb") as f:
            page = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(page)

    def do_POST(self):
        # the page POSTs "dx,dy" — forward it VERBATIM to the mouse receiver.
        # the bridge never parses it: same protocol, just changing trains.
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n)
        udp.sendto(body, ("127.0.0.1", 9999))
        self.send_response(204)
        self.end_headers()

    def log_message(self, *args):
        pass  # keep the console quiet at 60 requests/sec

httpd = http.server.ThreadingHTTPServer(("0.0.0.0", 8443), Handler)
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain(os.path.join(HERE, "cert.pem"), os.path.join(HERE, "key.pem"))
httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)

print("bridge running — on your phone, open:  https://192.168.1.251:8443")
httpd.serve_forever()
