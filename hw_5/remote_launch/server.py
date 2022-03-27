import socket
import os

server_address = '127.168.3.5'
server_port = 99
BUFF_SIZE = 4096

def recvall(connect):
    byte_message = bytearray()
    while True:
        part_message = connect.recv(BUFF_SIZE)
        byte_message.extend(part_message)
        if len(part_message) < BUFF_SIZE:
            break
    return byte_message

server = socket.socket()
server.bind((server_address, server_port))
server.listen()

while True:
    connect, _ = server.accept()
    command = recvall(connect).decode('utf-8')
    print('Command from user: {}'.format(command))
    os.system(command)
    connect.close()
