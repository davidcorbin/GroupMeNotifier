from distutils.core import setup
import requests.certs

build_exe_options = {"include_files": [(requests.certs.where(), 'cacert.pem')]}

setup(
    name='GroupMe Notifier',
    version='0.1',
    packages=['groupmenotifier'],
    url='http://daconex.me',
    license='MIT',
    author='David Corbin',
    author_email='daconex+groupmenotifier@gmail.com',
    description='Client for GroupMe',
    install_requires=['requests', 'websocket']
)
