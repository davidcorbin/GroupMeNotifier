from distutils.core import setup
from cx_Freeze import setup, Executable
import requests.certs
import sys
import os

print os.getcwd()+"\\groupmenotifier"
sys.path.append(os.getcwd()+"\\groupmenotifier")

options = {
    'build_exe': {
        'includes': ["groupme"],
        'include_files': [(requests.certs.where(), 'cacert.pem')]
    }
}

setup(
    name='GroupMe Notifier',
    version='0.1',
    url='http://daconex.me',
    license='MIT',
    author='David Corbin',
    author_email='daconex+groupmenotifier@gmail.com',
    description='Client for GroupMe',
    options=options,
    executables=[Executable("groupmenotifier/main.py")]
)
