from distutils.core import setup
from cx_Freeze import setup, Executable
import requests.certs
import sys
import os

# Added groupmenotifier/ directory to system path so thay cxfreeze includes groupme.py, etc.
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
    description='Windows 10 client for GroupMe',
    options=options,
    executables=[Executable("groupmenotifier/main.py")],
    requires=['requests', 'cx_Freeze']
)
