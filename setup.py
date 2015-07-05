#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
########################################################################
# Copyright 2015 Matthieu Gaignière                  http://lightcode.fr
########################################################################
# This file is part of OVM.
#
# OVM is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# OVM is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with OVM. If not, see <http://www.gnu.org/licenses/>.
########################################################################


import os
import shutil
from setuptools import setup, find_packages

from ovm.app import App


with open('requirements.txt') as f:
    requirements = [line.strip() for line in f.readlines()]

setup(
    name='OVM',
    version=App.VERSION,
    description='Open Virtualization Manager',
    author='Matthieu Gaigniere',
    author_email='matthieu@lightcode.fr',
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

if os.path.exists(App.ETC):
    print("Don't change {0}".format(App.ETC))
else:
    shutil.copytree('etc/', '/etc/ovm')

if not os.path.exists(App.SAVED_VMS):
    os.makedirs(App.SAVED_VMS)

DEFAULT_STORAGE_POOL = '/var/lib/ovm/storage-pools/default'
if not os.path.exists(DEFAULT_STORAGE_POOL):
    os.makedirs(DEFAULT_STORAGE_POOL)
