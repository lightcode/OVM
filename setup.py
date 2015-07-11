#!/usr/bin/env python3

import os
import shutil
from setuptools import setup, find_packages

from ovm.configuration import Configuration


with open('requirements.txt') as f:
    requirements = [line.strip() for line in f.readlines()]

setup(
    name='OVM',
    version=Configuration.VERSION,
    description='Open Virtualization Manager',
    author='Matthieu Gaignière',
    author_email='lightcode@gmx.com',
    url='http://lightcode.fr',
    install_requires=requirements,
    packages=find_packages(),
    data_files=[
        ('/etc/bash_completion.d', ['bin/vm-completion'])
    ],
    entry_points={
        'console_scripts': ['vm = ovm.vmcli.__main__:main']
    }
)

if os.path.exists(Configuration.ETC):
    print("Don't change {0}".format(Configuration.ETC))
else:
    shutil.copytree('etc/', '/etc/ovm')

if not os.path.exists(Configuration.SAVED_VMS):
    os.makedirs(Configuration.SAVED_VMS)

DEFAULT_STORAGE_POOL = '/var/lib/ovm/storage-pools/default'
if not os.path.exists(DEFAULT_STORAGE_POOL):
    os.makedirs(DEFAULT_STORAGE_POOL)
