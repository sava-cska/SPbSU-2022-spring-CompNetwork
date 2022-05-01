import socket
from datetime import datetime

server_address = '127.168.3.5'
server_port = 97
BUFF_SIZE = 4096
TOTAL_PACKAGES = 10
TIMEOUT = 1

echo_client = socket.socket(type=socket.SOCK_DGRAM)
echo_client.settimeout(TIMEOUT)
server = (server_address, server_port)

min_rtt, max_rtt, sum_rtt, success_package = 0, 0, 0, 0
for num in range(TOTAL_PACKAGES):
    message = 'Ping {} {}'.format(num, datetime.now())
    print('Client sends to {}: {}'.format(server, message))
    start_time = datetime.now()
    echo_client.sendto(bytes(message, 'utf-8'), server)

    try:
        answer, server_address = echo_client.recvfrom(BUFF_SIZE)
        finish_time = datetime.now()
        rtt = (finish_time - start_time).total_seconds()

        answer = answer.decode('utf-8')
        print('Client receives from {}: {}'.format(server_address, answer))
        print('Time: {} seconds'.format(rtt))

        success_package += 1
        sum_rtt += rtt
        if success_package == 1:
            min_rtt, max_rtt = rtt, rtt
        else:
            min_rtt = min(min_rtt, rtt)
            max_rtt = max(max_rtt, rtt)
    except socket.timeout as exc:
        print('Request timed out')
    print()

print('--------------------------------')
print('Minimum rtt: {} seconds'.format(min_rtt))
print('Maximum rtt: {} seconds'.format(max_rtt))
print('Average rtt: {} seconds'.format(sum_rtt / success_package))
print('Lost {0:.1%} of packages'.format(1 - success_package / TOTAL_PACKAGES))
