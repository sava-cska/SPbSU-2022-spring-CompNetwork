import netifaces
import socket

for interface in netifaces.interfaces():
    addresses = netifaces.ifaddresses(interface)
    if netifaces.AF_INET in addresses and addresses[netifaces.AF_INET][0]['addr'] != socket.gethostbyname('localhost'):
        print('My IP address: {}, network mask: {}'.format(addresses[netifaces.AF_INET][0]['addr'], addresses[netifaces.AF_INET][0]['netmask']))