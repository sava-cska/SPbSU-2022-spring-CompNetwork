import socket
from datetime import datetime
import sys
import time

server_address = '127.168.3.5'
server_port = 97
TIMEOUT = 1

client = socket.socket(type=socket.SOCK_DGRAM)
server = (server_address, server_port)

total_packages = int(sys.argv[1])
for num in range(total_packages):
    message = 'Ping {} {}'.format(num, datetime.now())
    print('Client sends to {}: {}'.format(server, message))
    client.sendto(bytes(message, 'utf-8'), server)
    time.sleep(TIMEOUT)

