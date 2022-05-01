import argparse
from ftplib import FTP
from pathlib import Path, PurePosixPath

server_address = '127.0.0.1'
user_name = 'TestUser'
password = '12345'

def show_content(args):
    server_path = PurePosixPath(args.path[0])
    with FTP(host=server_address, user=user_name, passwd=password) as ftp:
        print('Content of {}'.format(server_path))
        ftp.dir(str(server_path))

def upload_file(args):
    local_path = Path(args.local_path[0])
    server_path = PurePosixPath(args.server_path[0])
    with FTP(host=server_address, user=user_name, passwd=password) as ftp:
        ftp.cwd(str(server_path.parent))
        with open(local_path, 'rb') as file:
            ftp.storbinary('STOR {}'.format(server_path.name), file)
        print('Upload file {}'.format(local_path))

def download_file(args):
    local_path = Path(args.local_path[0])
    server_path = PurePosixPath(args.server_path[0])
    with FTP(host=server_address, user=user_name, passwd=password) as ftp:
        ftp.cwd(str(server_path.parent))
        with open(local_path, 'wb') as file:
            ftp.retrbinary('RETR {}'.format(server_path.name), file.write)
        print('Download file {}'.format(local_path))

def create_parser():
    parser = argparse.ArgumentParser(description='Console FTP client.')
    subparsers = parser.add_subparsers()

    show_parser = subparsers.add_parser('show', help='Show content of directory.')
    show_parser.add_argument(
        'path',
        nargs=1,
        type=str,
        help='Path to directory on ftp server.',
    )
    show_parser.set_defaults(func=show_content)

    upload_parser = subparsers.add_parser('upload', help='Upload file to ftp server.')
    upload_parser.add_argument(
        'local_path',
        nargs=1,
        type=str,
        help='Local path to file.',
    )
    upload_parser.add_argument(
        'server_path',
        nargs=1,
        type=str,
        help='Server path to destination.'
    )
    upload_parser.set_defaults(func=upload_file)

    download_parser = subparsers.add_parser('download', help='Download file from ftp server.')
    download_parser.add_argument(
        'server_path',
        nargs=1,
        type=str,
        help='Server path to file.',
    )
    download_parser.add_argument(
        'local_path',
        nargs=1,
        type=str,
        help='Local path to destination.',
    )
    download_parser.set_defaults(func=download_file)
    
    return parser

if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    args.func(args)