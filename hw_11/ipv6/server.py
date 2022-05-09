import socket
import sys

BUFF_SIZE = 4096

server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
server_ip = sys.argv[1]
server_port = int(sys.argv[2])
server_address = (server_ip, server_port)
server.bind(server_address)
server.listen()

while True:
    connect, client_address = server.accept()
    message = connect.recv(BUFF_SIZE)
    print('Receive from {} message = {}'.format(client_address, message.decode('utf-8')))

    answer = bytes(message.decode('utf-8').upper(), 'utf-8')
    connect.sendall(answer)
    print('Send to {} message = {}'.format(client_address, answer.decode('utf-8')))

    connect.close()