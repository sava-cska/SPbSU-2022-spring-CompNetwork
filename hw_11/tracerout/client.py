import socket
import sys
import struct
from datetime import datetime

BUFF_SIZE = 4096
TRACEROUTE_ID = 1000
TIMEOUT = 1

class ICMP_exception(Exception):
    def __init__(self, msg):
        super().__init__(msg)

def count_checksum(bytes):
    idx = 0
    sum = 0
    while idx < len(bytes):
        num = int.from_bytes(bytes[idx:(idx + 2)], byteorder='little', signed=False)
        sum = (sum + num) & ((1 << 32) - 1)
        idx += 2
    sum = (sum >> 16) + (sum & ((1 << 16) - 1))
    sum = (sum >> 16) + (sum & ((1 << 16) - 1))
    return (1 << 16) - 1 - sum

def create_icmp_header(head_type, head_code, head_checksum, head_id, head_seqnum):
    return struct.pack('BBHHH', head_type, head_code, head_checksum, head_id, head_seqnum)

def create_message(seq_num):
    header = create_icmp_header(8, 0, 0, TRACEROUTE_ID, seq_num)
    checksum = count_checksum(header)
    header = create_icmp_header(8, 0, checksum, TRACEROUTE_ID, seq_num)
    return header

def icmp_number(message, lef, rig):
    return int.from_bytes(message[lef:rig], byteorder='little', signed=False)

def icmp_type_and_code(message):
    return icmp_number(message, 20, 21), icmp_number(message, 21, 22)

def icmp_id_and_seqnum(message):
    return icmp_number(message, 24, 26), icmp_number(message, 26, 28)

def send_icmp(host, server_name, seq_num, ttl):
    message = create_message(seq_num)
    host.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, struct.pack('B', ttl))
    host.sendto(message, (server_name, 1))

def receive_icmp(host, seq_num):
    while True:
        answer, answer_host = host.recvfrom(BUFF_SIZE)
        ans_type, ans_code = icmp_type_and_code(answer)
        if ans_type == 0 and ans_code == 0:
            ans_id, ans_seqnum = icmp_id_and_seqnum(answer)
            if ans_id == TRACEROUTE_ID and ans_seqnum == seq_num:
                break
        elif ans_type == 11 and ans_code == 0:
                break
        else:
            raise ICMP_exception('Error. ICMP type = {}, icmp code = {}'.format(ans_type, ans_code))

    return ans_type, answer_host[0]

if __name__ == '__main__':
    traceroute_host = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
    traceroute_host.settimeout(TIMEOUT)

    server_name = sys.argv[1]
    message_num = int(sys.argv[2])
    
    seq_num, ttl = 0, 0
    destination = False
    while not destination:
        ttl += 1
        print('TTL = {}'.format(ttl), end=', ')
        for i in range(message_num):
            seq_num += 1
            start = datetime.now()
            send_icmp(traceroute_host, server_name, seq_num, ttl)
            
            try:
                ans_type, answer_host = receive_icmp(traceroute_host, seq_num)
                finish = datetime.now()
                if ans_type == 0:
                    destination = True
                if i == 0:
                    try:
                        ans_name_host = socket.gethostbyaddr(answer_host)[0]
                        print('host = {} [{}]:'.format(ans_name_host, answer_host), end=' ')
                    except socket.herror:
                        print('host = {}:'.format(answer_host), end=' ')
                print('{:.4}ms'.format((finish - start).total_seconds() * 1000), end=', ')
            
            except socket.timeout as exc:
                if i == 0:
                    print('host = ***:', end = ' ')
                print('Timeout', end=', ')
            except BaseException as exc:
                print(exc)
        print()
    
    traceroute_host.close()
