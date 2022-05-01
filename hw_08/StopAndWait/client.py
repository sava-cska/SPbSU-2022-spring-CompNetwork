import socket
import more_itertools
import numpy
import sys
from checksum.checksum import count_checksum, check_checksum

LOST_MESSAGE = 0.3

class Client(object):
    def __init__(self, server_address, server_port, timeout):
        self.server_address = server_address
        self.server_port = server_port
        self.buff_size = 4096
        self.timeout = timeout
    
    def open(self):
        try:
            self.client = socket.socket(type=socket.SOCK_DGRAM)
            print('Open client socket with timeout = {}s.'.format(self.timeout))
        except BaseException as exc:
            print("Can't create client socket.")
            print(exc)
            raise
    
    def close(self):
        try:
            self.client.close()
            print('Close client socket.')
        except BaseException as exc:
            print("Can't close server socket.")
            print(exc)
            raise
    
    def send_segment(self, segment, type_m):
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
            self.client.sendto(message, (self.server_address, self.server_port))
            print('Send to ({}, {}) message = {}.'.format(self.server_address, self.server_port, message))
            try:
                answer, _ = self.client.recvfrom(self.buff_size)
                rnd = numpy.random.random()
                if rnd > LOST_MESSAGE:
                    print('Receive from ({}, {}) message = {}.'.format(self.server_address, self.server_port, answer))
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

    def send_message(self, byte_array):
        self.client.settimeout(self.timeout)
        
        segments = list(more_itertools.windowed(byte_array, self.buff_size - 3, step=self.buff_size - 3))
        if segments[-1][-1] is not None:
            segments.append((None, ) * (self.buff_size - 3))
        
        type_m = 0
        for idx, segment in enumerate(segments):
            print('Send segment {}/{}.'.format(idx + 1, len(segments)))
            self.send_segment(segment, type_m)
            type_m = 1 - type_m
        
        self.client.settimeout(None)

    def receive_message(self):
        message = bytearray()
        type_m = 0
        while True:
            try:
                segment, server_address = self.client.recvfrom(self.buff_size)
                rnd = numpy.random.random()
                if rnd < LOST_MESSAGE:
                    print('Lose message.')
                    continue
                print('Receive from {} message = {}'.format(server_address, segment))

                if not check_checksum(segment[2:], int.from_bytes(segment[:2], byteorder='little', signed=False)):
                    continue
                
                ans_mes = bytearray([segment[2]])
                ans_mes = count_checksum(ans_mes).to_bytes(2, byteorder='little', signed=False) + ans_mes
                self.client.sendto(ans_mes, server_address)
                print('Send to {} message = {}'.format(server_address, ans_mes))

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

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Wrong number of arguments.')
        quit()
    
    server_address = sys.argv[1]
    server_port = int(sys.argv[2])
    timeout = int(sys.argv[3])

    client = Client(server_address, server_port, timeout)
    with open('example/client_message.txt', 'rb') as file:
        message = file.read()
    client.open()
    client.send_message(message)

    message = client.receive_message()
    with open('example/client_pic.jpg', 'wb') as file:
        file.write(message)
    client.close()