from datetime import datetime
import socket
import numpy

server_address = '127.168.3.5'
server_port = 97
BUFF_SIZE = 4096
LOST_MESSAGE = 5
TIMEOUT = 1
TIMEOUT_DEAD_SERVER = 10

heartbeat_server = socket.socket(type=socket.SOCK_DGRAM)
heartbeat_server.bind((server_address, server_port))
heartbeat_server.settimeout(TIMEOUT)

clients = {}
while True:
    try:
        message, client_address = heartbeat_server.recvfrom(BUFF_SIZE)
        message = message.decode('utf-8')
        print('Server receives from {}: {}'.format(client_address, message))

        rnd = numpy.random.randint(LOST_MESSAGE)
        if rnd != 0:
            clients[client_address] = datetime.now()
    except socket.timeout as exc:
        pass
    
    cur_time = datetime.now()
    clients_list = list(clients.items())
    for client, last_time in clients_list:
        if (cur_time - last_time).total_seconds() > TIMEOUT_DEAD_SERVER:
            print('{} is dead'.format(client))
            clients.pop(client)

