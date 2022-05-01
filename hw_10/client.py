import socket
import sys
import struct
from datetime import datetime
import time

BUFF_SIZE = 4096
TOTAL_PACKAGES = 4
PING_ID = 1000

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
    header = create_icmp_header(8, 0, 0, PING_ID, seq_num)
    data = bytes(str(datetime.now()), 'utf-8')
    checksum = count_checksum(header + data)
    header = create_icmp_header(8, 0, checksum, PING_ID, seq_num)
    return header + data

def icmp_number(message, lef, rig):
    return int.from_bytes(message[lef:rig], byteorder='little', signed=False)

def icmp_type_and_code(message):
    return icmp_number(message, 20, 21), icmp_number(message, 21, 22)

def icmp_id_and_seqnum(message):
    return icmp_number(message, 24, 26), icmp_number(message, 26, 28)

def send_icmp(host, server_name, seq_num):
    message = create_message(seq_num)
    host.sendto(message, (server_name, 1))

def receive_icmp(host, seq_num):
    while True:
        answer, _ = host.recvfrom(BUFF_SIZE)

        ans_type, ans_code = icmp_type_and_code(answer)
        if ans_type == 0 and ans_code == 0:
            ans_id, ans_seqnum = icmp_id_and_seqnum(answer)
            if ans_id == PING_ID and ans_seqnum == seq_num:
                break
        elif ans_type == 3:
            if ans_code == 0:
                raise ICMP_exception('Destination Unreachable. Destination network unreachable.')
            elif ans_code == 1:
                raise ICMP_exception('Destination Unreachable. Destination host unreachable.')
            elif ans_code == 2:
                raise ICMP_exception('Destination Unreachable. Destination protocol unreachable.')
            elif ans_code == 3:
                raise ICMP_exception('Destination Unreachable. Destination port unreachable.')
            else:
                raise ICMP_exception('Unknown error. ICMP type = {}, icmp code = {}'.format(ans_type, ans_code))
        elif ans_type == 11:
            if ans_code == 0:
                raise ICMP_exception('Time Exceeded. TTL expired in transit.')
            elif ans_code == 1:
                raise ICMP_exception('Time Exceeded. Fragment reassembly time exceeded.')
            else:
                raise ICMP_exception('Unknown error. ICMP type = {}, icmp code = {}'.format(ans_type, ans_code))
        elif ans_type == 12:
            if ans_code == 0:
                raise ICMP_exception('Parameter Problem: Bad IP header. Pointer indicates the error.')
            elif ans_code == 1:
                raise ICMP_exception('Parameter Problem: Bad IP header. Missing a required option.')
            elif ans_code == 2:
                raise ICMP_exception('Parameter Problem: Bad IP header. Bad length.')
            else:
                raise ICMP_exception('Unknown error. ICMP type = {}, icmp code = {}'.format(ans_type, ans_code))
        else:
            raise ICMP_exception('Unknown error. ICMP type = {}, icmp code = {}'.format(ans_type, ans_code))
            
    
    data = datetime.strptime(answer[28:].decode('utf-8'), '%Y-%m-%d %H:%M:%S.%f')
    rtt = datetime.now() - data
    return rtt

if __name__ == '__main__':
    ping_host = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
    ping_host.settimeout(1)

    server_name = sys.argv[1]
    
    min_rtt, max_rtt, sum_rtt, suc_pack = 0, 0, 0, 0
    for i in range(TOTAL_PACKAGES):
        time.sleep(1)

        send_icmp(ping_host, server_name, i)
        try:
            rtt = receive_icmp(ping_host, i).total_seconds()
            print('Iteration {} from {}: rtt = {} seconds.'.format(i + 1, TOTAL_PACKAGES, rtt))

            if suc_pack == 0:
                min_rtt, max_rtt = rtt, rtt
            min_rtt = min(min_rtt, rtt)
            max_rtt = max(max_rtt, rtt)
            sum_rtt += rtt
            suc_pack += 1
        except socket.timeout as exc:
            print('Request timed out.')
        except ICMP_exception as exc:
            print(exc)
    
    if suc_pack != 0:
        avg_rtt = sum_rtt / suc_pack
    else:
        avg_rtt = 0.0

    print('Minimum rtt: {} seconds.'.format(min_rtt))
    print('Maximum rtt: {} seconds.'.format(max_rtt))
    print('Average rtt: {:.5} seconds.'.format(avg_rtt))
    print('Lost {0:.1%} of packages.'.format(1 - suc_pack / TOTAL_PACKAGES))

    ping_host.close()