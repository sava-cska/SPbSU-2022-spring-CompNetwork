import socket
import sys

server_address = '127.168.3.5'
server_port = 99
BUFF_SIZE = 4096

client = socket.socket()
client.connect((server_address, server_port))
command = sys.argv[1]
print('Command for server: {}'.format(command))
client.sendall(bytes(command, 'utf-8'))
client.close()
