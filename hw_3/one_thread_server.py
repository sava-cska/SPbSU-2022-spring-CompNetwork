import socket
import os.path

serverAddress = '127.168.3.5'
serverPort = 1010
BUFF_SIZE = 4096

server = socket.socket()
server.bind((serverAddress, serverPort))
server.listen()

while True:
    connect, (address, port) = server.accept()
    http_req = connect.recv(BUFF_SIZE)
    decoded_req = http_req.decode('utf-8')
    print(decoded_req)
    path_to_file = '.' + decoded_req.split(' ')[1]

    if os.path.exists(path_to_file):
        with open(path_to_file, 'r', encoding='utf-8') as file:
            content = ''.join(file.readlines()).replace('\n', '\r\n')
        text = bytes('HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n' + content, 'utf-8')
    else:
        text = bytes('HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n404 Not Found', 'utf-8')
    connect.sendall(text)
    connect.close()
