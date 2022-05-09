import socket
import sys

BUFF_SIZE = 4096

client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
server_ip = sys.argv[1]
server_port = int(sys.argv[2])
server_address = (server_ip, server_port)

client.connect(server_address)
message = bytes('Hello from MKN!', 'utf-8')
client.sendall(message)
print('Send to {} message = {}'.format(server_address, message.decode('utf-8')))

answer = client.recv(BUFF_SIZE)
print('Receive from {} message = {}'.format(server_address, answer.decode('utf-8')))

client.close()