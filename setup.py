#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import sys
from setuptools import setup, find_packages

from ovm.configuration import Configuration


requirements = ['pyaml', 'six']

if sys.version_info.major == 2:
    requirements.append('futures')

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
        ('bash_completion.d', ['bin/vm-completion'])
    ],
    entry_points={
        'console_scripts': ['vm = ovm.vmcli.__main__:main']
    }
)

if not os.path.exists(Configuration.ETC):
    shutil.copytree('etc/', Configuration.ETC)

if not os.path.exists(Configuration.SAVED_VMS):
    os.makedirs(Configuration.SAVED_VMS)
