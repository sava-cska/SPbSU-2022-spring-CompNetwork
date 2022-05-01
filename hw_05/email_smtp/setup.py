from importlib_metadata import entry_points
from setuptools import setup

setup(
    name='email_smtp',
    version='1.0.0', 
    packages=['client_smtplib', 'client_socket'],
    entry_points={
        'console_scripts': [
            'send_with_smtplib=client_smtplib.client:main',
            'send_with_socket=client_socket.client:main',
        ],
    },
)