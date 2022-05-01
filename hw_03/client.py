import socket
import sys

serverAddress = sys.argv[1]
serverPort = int(sys.argv[2])
fileName = sys.argv[3]
BUFF_SIZE = 4096

client = socket.socket()
client.connect((serverAddress, serverPort))
request = bytes('GET /{0} HTTP/1.1\r\nHost: {1}:{2}\r\n\r\n'.format(fileName, serverAddress, serverPort), 'utf-8')
print(request)
client.sendall(request)
response = client.recv(BUFF_SIZE)
print(response)
client.close()