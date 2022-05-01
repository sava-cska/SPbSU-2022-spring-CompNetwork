import socket
import more_itertools
import numpy
import sys
from checksum.checksum import count_checksum, check_checksum

LOST_MESSAGE = 0.3

class Server(object):
    def __init__(self, server_address, server_port, timeout):
        self.server_address = server_address
        self.server_port = server_port
        self.buff_size = 4096
        self.timeout = timeout
    
    def open(self):
        try:
            self.server = socket.socket(type=socket.SOCK_DGRAM)
            self.server.bind((self.server_address, self.server_port))
            print('Open server socket ({}, {}).'.format(self.server_address, self.server_port))
        except BaseException as exc:
            print("Can't create server socket.")
            print(exc)
            raise
    
    def close(self):
        try:
            self.server.close()
            print('Close server socket.')
        except BaseException as exc:
            print("Can't close server socket.")
            print(exc)
            raise
    
    def receive_message(self):
        message = bytearray()
        type_m = 0
        while True:
            try:
                segment, client_address = self.server.recvfrom(self.buff_size)
                rnd = numpy.random.random()
                if rnd < LOST_MESSAGE:
                    print('Lose message.')
                    continue
                print('Receive from {} message = {}'.format(client_address, segment))
                
                if not check_checksum(segment[2:], int.from_bytes(segment[:2], byteorder='little', signed=False)):
                    continue

                ans_mes = bytearray([segment[2]])
                ans_mes = count_checksum(ans_mes).to_bytes(2, byteorder='little', signed=False) + ans_mes
                self.server.sendto(ans_mes, client_address)
                print('Send to {} message = {}'.format(client_address, ans_mes))

                if segment[2] == type_m:
                    message.extend(segment[3:])
                    type_m = 1 - type_m
                if len(segment) < self.buff_size:
                    break
            except socket.error as exc:
                print('Socket exception.')
                print(exc)
                raise
            except BaseException as exc:
                print(exc)
        return message
    
    def send_segment(self, segment, type_m, client_address, client_port):
        message = bytearray()
        message.append(type_m)
        for one_byte in segment:
            if one_byte is None:
                break
            message.append(one_byte)
        
        checksum = count_checksum(message)
        message = checksum.to_bytes(2, byteorder='little', signed=False) + message
        
        segment_received = False
        while not segment_received:
            self.server.sendto(message, (client_address, client_port))
            print('Send to ({}, {}) message = {}.'.format(client_address, client_port, message))
            try:
                answer, _ = self.server.recvfrom(self.buff_size)
                rnd = numpy.random.random()
                if rnd > LOST_MESSAGE:
                    print('Receive from ({}, {}) message = {}.'.format(client_address, client_port, answer))
                    if len(answer) == 3 and answer[2] == type_m and check_checksum(answer[2:], int.from_bytes(answer[:2], byteorder='little', signed=False)):
                        segment_received = True
                else:
                    print('Lose message.')
            except socket.timeout as exc:
                print('Request timed out.')
            except socket.error as exc:
                print('Socket exception.')
                print(exc)
                raise
            except BaseException as exc:
                print(exc)

    def send_message(self, byte_array, client_address, client_port):
        self.server.settimeout(self.timeout)
        
        segments = list(more_itertools.windowed(byte_array, self.buff_size - 3, step=self.buff_size - 3))
        if segments[-1][-1] is not None:
            segments.append((None, ) * (self.buff_size - 3))
        
        type_m = 0
        for idx, segment in enumerate(segments):
            print('Send segment {}/{}.'.format(idx + 1, len(segments)))
            self.send_segment(segment, type_m, client_address, client_port)
            type_m = 1 - type_m
        
        self.server.settimeout(None)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Wrong number of arguments.')
        quit()
    
    server_address = sys.argv[1]
    server_port = int(sys.argv[2])
    timeout = int(sys.argv[3])

    server = Server(server_address, server_port, timeout)
    server.open()
    
    message = server.receive_message()
    with open('example/server_message.txt', 'wb') as file:
        file.write(message)

    args = input().split()
    client_address, client_port = args[0], int(args[1])
    with open('example/server_pic.jpg', 'rb') as file:
        message = file.read()
    server.send_message(message, client_address, client_port)

    server.close()