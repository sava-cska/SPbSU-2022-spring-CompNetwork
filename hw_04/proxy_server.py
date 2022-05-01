import socket
from threading import Thread, Lock

BUFF_SIZE = 4096
HTTP_PORT = 80
HISTORY_FILE = 'history.txt'
BLACK_LIST_FILE = 'black_list.txt'
MODIFY_REQUEST = 'GET {} HTTP/1.1\r\nHost: {}\r\nIf-Modified-Since: {}\r\nIf-None-Match: {}\r\n\r\n'
HOSTNAME_TO_ETAG = {}
HOSTNAME_TO_DATE = {}
CASH_LOCK = Lock()
HISTORY_LOCK = Lock()
black_list = []

def recvall(connect):
    byte_message = bytearray()
    while True:
        part_message = connect.recv(BUFF_SIZE)
        byte_message.extend(part_message)
        if len(part_message) < BUFF_SIZE:
            break
    return byte_message

def create_filename(url, etag):
    return 'cash/__{}__{}__'.format(url, etag.replace('"', '_'))

def add_to_magazine(url, response_code):
    HISTORY_LOCK.acquire()
    history = open(HISTORY_FILE, 'a', encoding='utf-8')
    history.write('({}, {})\r\n'.format(url, response_code))
    history.close()
    HISTORY_LOCK.release()

def thread_client(client):
    print('------------------------')

    decoded_req = recvall(client).decode('utf-8')

    print('Request to proxy server:')
    print('------------------------')
    print(decoded_req)
    print('------------------------')

    hostname = ''
    try:
        blocks = decoded_req.split('\r\n\r\n')
        headers = blocks[0].split('\r\n')
        status_line = headers[0].split(' ')
        address_request = status_line[1].split('/')
        url = address_request[1]
        other_addr = '/{}'.format('/'.join(address_request[2:]))
        headers[0] = '{} {} {}'.format(status_line[0], other_addr, ' '.join(status_line[2:]))
        for idx, line in enumerate(headers):
            if line.startswith('Host:'):
                headers[idx] = 'Host: {}'.format(url)
        blocks[0] = '\r\n'.join(headers)
        target_request = '\r\n\r\n'.join(blocks)

        if status_line[0] == 'GET':
            hostname = status_line[1]
    except BaseException as err:
        print('Incorrect http request')
        print(err)
        print('------------------------')
        client.close()
        return

    if url in black_list:
        add_to_magazine(url, 403)
        print('This site in black list')
        print('------------------------')
        
        message = 'HTTP/1.1 403 Forbidden\r\nContent-Type: text/html; charset=UTF-8\r\n\r\nThis site is in black list.\r\n'
        client.sendall(bytes(message, 'utf-8'))
        client.close()
        return

    CASH_LOCK.acquire()
    existence = hostname in HOSTNAME_TO_ETAG
    CASH_LOCK.release()

    if existence:
        etag = HOSTNAME_TO_ETAG[hostname]
        last_mod = HOSTNAME_TO_DATE[hostname]

        print('Check last modified date')
        print('------------------------')     

        status_socket = socket.socket()
        status_socket.connect((url, HTTP_PORT))
        status_request = MODIFY_REQUEST.format(other_addr, url, last_mod, etag)
        status_socket.sendall(bytes(status_request, 'utf-8'))
        status_response = recvall(status_socket).decode('utf-8')
        status_socket.close()

        print('Status request to server:')
        print('------------------------')
        print(status_request)
        print('------------------------')

        print('Status response from server:')
        print('------------------------')
        print(status_response)
        print('------------------------')
        
        try:
            if status_response.split(' ')[1] == '304':
                filename = create_filename(url, etag)
                response_file = open(filename, 'rb')
                server_response = response_file.read().decode('utf-8')
                response_file.close()

                print('Response from server:')
                print('------------------------')
                print(server_response)
                print('------------------------')

                add_to_magazine(url, 304)

                client.sendall(bytes(server_response, 'utf-8'))
                client.close()
                return
        except BaseException as err:
            print('Incorrect status response')
            print(err)
            print('------------------------')
            client.close()
            return

    print('Request to server:')
    print('------------------------')
    print(target_request)
    print('------------------------')

    target_server = socket.socket()
    server_response = bytearray()
    try:
        target_server.connect((url, HTTP_PORT))
        target_server.sendall(bytes(target_request, 'utf-8'))
        server_response = recvall(target_server)
    except BaseException as err:
        print("Server doesn't connect to {}".format(url))
        print(err)
        print('------------------------')
    target_server.close()

    print('Response from server:')
    print('------------------------')
    print(server_response.decode('utf-8'))
    print('------------------------')

    try:
        response_code = int(server_response.decode('utf-8').split(' ')[1])
        add_to_magazine(url, response_code)

        blocks = server_response.decode('utf-8').split('\r\n\r\n')
        headers = blocks[0].split('\r\n')
        etag = ''
        last_mod = ''
        for line in headers:
            if line.startswith('ETag: '):
                etag = line.split(' ')[1]
            if line.startswith('Last-Modified: '):
                last_mod = ' '.join(line.split(' ')[1:])
        
        print('ETag: {} and hostname: {}'.format(etag, hostname))
        print('------------------------')
        if etag != '' and hostname != '':
            CASH_LOCK.acquire()
            HOSTNAME_TO_DATE[hostname] = last_mod
            HOSTNAME_TO_ETAG[hostname] = etag
            filename = create_filename(url, etag)
            response_file = open(filename, 'wb')
            response_file.write(server_response)
            response_file.close()
            CASH_LOCK.release()

    except BaseException as err:
        print('Incorrect http response')
        print(err)
        print('------------------------')
        client.close()
        return

    client.sendall(server_response)
    client.close()

proxyAddress = '127.168.3.5'
proxyPort = 1010

proxy_server = socket.socket()
proxy_server.bind((proxyAddress, proxyPort))
proxy_server.listen()

history = open(HISTORY_FILE, 'w', encoding='utf-8')
history.close()
black_list_file = open(BLACK_LIST_FILE, 'r', encoding='utf-8')
black_list = black_list_file.read().split('\n')
black_list_file.close()
while True:
    client, _ = proxy_server.accept()
    thread = Thread(target=thread_client, args=(client,))
    thread.start()