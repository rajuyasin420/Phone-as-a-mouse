import socket
from pynput.mouse import Controller

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # make socket — ONCE
client.bind(("0.0.0.0", 9999))                             # 'client', not 'socket' — ONCE
print("listening on 9999...")
mouse = Controller()                           # factory result CAUGHT in a variable

while True:                                    # loop forever
    message, address = client.recvfrom(1024)   # blocks until a packet arrives
    try:
        msg = message.decode('utf-8')          # bytes -> string ('message' owns the dot)
        two = msg.split(",")                   # comma: the delimiter our protocol promised
        dx = float(two[0])
        dy = float(two[1])
        mouse.move(dx, dy)                     # the point of the whole file
    except (ValueError, IndexError):           # bad packet? skip it, don't die
        continue
