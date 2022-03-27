import argparse
import socket
import base64
import ssl

BUFF_SIZE = 4096

smtp_host = 'smtp.mail.ru'
smtp_port = 465
username = 'vasya-pupkin@gmail.com'
password = '123456'

sender_address = 'vasya-pupkin@gmail.com'
email_subject = 'Very important email'
text_message_template = \
'''\
From: {}
To: {}
Subject: {}
Content-Type: text/plain; charset="utf-8"

{}
'''

image_message_template = \
'''\
From: {}
To: {}
Subject: {}
Content-Type: image/jpeg; name={}
Content-Transfer-Encoding: base64

'''

def recvall(connect):
    byte_message = bytearray()
    while True:
        part_message = connect.recv(BUFF_SIZE)
        byte_message.extend(part_message)
        if len(part_message) < BUFF_SIZE:
            break
    return byte_message

def create_message(receiver_address, content_type, path_to_file):
    if content_type == 'text':
        with open(path_to_file, 'r', encoding='utf-8') as input_file:
            content = input_file.read()
        message = text_message_template.format(sender_address, receiver_address, email_subject, content)
        return bytes(message + '\r\n', 'utf-8')

    if content_type == 'image':
        with open(path_to_file, 'rb') as input_file:
            content = input_file.read()
        message = image_message_template.format(sender_address, receiver_address, email_subject, path_to_file.replace('/', '-'))
        return bytes(message, 'utf-8') + base64.b64encode(content) + bytes('\r\n', 'utf-8')

def send_recv_msg_and_check_code(client, raw_request, code, log_request=True):
    if raw_request is not None:
        if log_request:
            print('Request: {}'.format(raw_request.decode('utf-8')))
        client.sendall(raw_request)
    
    if code is not None:
        response = recvall(client).decode('ascii')
        print('Response: {}'.format(response))
        if not response.startswith(str(code)):
            raise ConnectionError("Return message doesn't start with needed code {}.\r\n Message: {}".format(code, response))

def delete_at_sign(email):
    index = email.find('@')
    return email[:index]

def send_email(receiver_address, content_type, path_to_file):
    client = socket.socket()
    client = ssl.wrap_socket(client)
    client.connect((smtp_host, smtp_port))

    # Приветственное сообщение
    send_recv_msg_and_check_code(client, None, 220)

    # HELO
    send_recv_msg_and_check_code(client, bytes('HELO {}\r\n'.format(delete_at_sign(receiver_address)), 'ascii'), 250)

    # AUTH LOGIN
    send_recv_msg_and_check_code(client, bytes('AUTH LOGIN\r\n', 'ascii'), 334)
    send_recv_msg_and_check_code(client, base64.b64encode(bytes(username, 'ascii')) + bytes('\r\n', 'ascii'), 334)
    send_recv_msg_and_check_code(client, base64.b64encode(bytes(password, 'ascii')) + bytes('\r\n', 'ascii'), 235)

    # MAIL From
    send_recv_msg_and_check_code(client, bytes('MAIL From: {}\r\n'.format(sender_address), 'ascii'), 250)
    
    # RCPT To
    send_recv_msg_and_check_code(client, bytes('RCPT To: {}\r\n'.format(receiver_address), 'ascii'), 250)

    # DATA
    send_recv_msg_and_check_code(client, bytes('DATA\r\n', 'ascii'), 354)

    # Сообщение
    raw_message = create_message(receiver_address, content_type, path_to_file)
    send_recv_msg_and_check_code(client, raw_message + bytes('.\r\n', 'utf-8'), 250, False)

    # QUIT
    send_recv_msg_and_check_code(client, bytes('QUIT', 'ascii'), None)
    client.close()

def main():
    parser = argparse.ArgumentParser(description='Send email with simple socket.')
    parser.add_argument(
        'receiver',
        nargs=1,
        type=str,
        help='Email address of receiver.',
    )
    parser.add_argument(
        '-type',
        nargs='?',
        default='text',
        type=str,
        choices=['text', 'image'],
        help="Type of content in email.",
    )
    parser.add_argument(
        '-file',
        nargs='?',
        default='examples/txt_email.txt',
        type=str,
        help='Path to file with body of email.',
    )

    args = parser.parse_args()
    send_email(args.receiver[0], args.type, args.file)