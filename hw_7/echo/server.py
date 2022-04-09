import socket
import numpy
import time

server_address = '127.168.3.5'
server_port = 97
BUFF_SIZE = 4096
LOST_MESSAGE = 5

echo_server = socket.socket(type=socket.SOCK_DGRAM)
echo_server.bind((server_address, server_port))

while True:
    message, client_address = echo_server.recvfrom(BUFF_SIZE)
    message = message.decode('utf-8')
    print('Server receives from {}: {}'.format(client_address, message))
    
    sleep_time = numpy.random.random()
    time.sleep(sleep_time)

    rnd = numpy.random.randint(LOST_MESSAGE)
    if rnd != 0:
        message = message.upper()
        print('Server sends to {}: {}'.format(client_address, message))
        echo_server.sendto(bytes(message, 'utf-8'), client_address)
    print()
