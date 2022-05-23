import netifaces
import socket
import ipaddress
import getmac

def get_local_address():
    for interface in netifaces.interfaces():
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses and addresses[netifaces.AF_INET][0]['addr'] != socket.gethostbyname('localhost'):
            return addresses[netifaces.AF_INET][0]['addr'], addresses[netifaces.AF_INET][0]['netmask']

def get_network_ip(ip, mask):
    elem1 = map(int, ip.split('.'))
    elem2 = map(int, mask.split('.'))
    res = map(lambda num: str(num[0] & num[1]), zip(elem1, elem2))
    return '.'.join(res)

my_ip, network_mask = get_local_address()
network_ip = get_network_ip(my_ip, network_mask)
network = ipaddress.IPv4Network('{}/{}'.format(network_ip, network_mask))

work_ip = [my_ip]
for ip_address in network.hosts():
    mac_address = getmac.get_mac_address(ip=ip_address.exploded)
    if mac_address and ip_address.exploded != my_ip:
        work_ip.append(ip_address.exploded)

for idx, ip_address in enumerate(work_ip):
    if idx == 0:
        print('My host')
    if idx == 1:
        print('Other hosts')    
    try:
        hostname, _, _ = socket.gethostbyaddr(ip_address)
    except BaseException as exc:
        hostname = 'Name not found'
    print('Host: {}, ip-address: {}, mac-address: {}'.format(hostname, ip_address, mac_address))