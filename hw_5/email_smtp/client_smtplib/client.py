import argparse
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
import ssl

smtp_host = 'smtp.mail.ru'
smtp_port = 465
username = 'vasya-pupkin@gmail.com'
password = '123456'

sender_address = 'vasya-pupkin@gmail.com'
email_subject = 'Very important email'

def create_message(receiver_address, text_type, path_to_file):
    with open(path_to_file, 'r', encoding='utf-8') as input_file:
        content = input_file.read()

    if text_type == 'txt':
        message = MIMEText(content, 'plain')
    if text_type == 'html':
        message = MIMEText(content, 'html')

    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = email_subject
    return message

def send_email(receiver_address, text_type, path_to_file):
    context = ssl.create_default_context()
    with SMTP_SSL(host=smtp_host, port=smtp_port, context=context) as smtp_server:
        smtp_server.login(username, password)
        message = create_message(receiver_address, text_type, path_to_file)
        smtp_server.sendmail(sender_address, receiver_address, message.as_string())

def main():
    parser = argparse.ArgumentParser(description='Send email with smtplib.')
    parser.add_argument(
        'receiver',
        nargs=1,
        type=str,
        help='Email address of receiver.',
    )
    parser.add_argument(
        '-type',
        nargs='?',
        default='txt',
        type=str,
        choices=['txt', 'html'],
        help='Type of email.',
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