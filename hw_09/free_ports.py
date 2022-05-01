import sys
import socket

def free_ports(ip_address, lef, rig):
    ports = []
    for port in range(lef, rig + 1):
        print('Check connection to port {}'.format(port))
        try:
            skt = socket.socket()
            skt.connect((ip_address, port))
            ports.append(port)
        except BaseException as _:
            pass
        finally:
            skt.close()
    return ports

if __name__ == '__main__':
    ip_address = sys.argv[1]
    lef_bound, rig_bound = int(sys.argv[2]), int(sys.argv[3])
    if lef_bound > rig_bound:
        lef_bound, rig_bound = rig_bound, lef_bound
    print(free_ports(ip_address, lef_bound, rig_bound))