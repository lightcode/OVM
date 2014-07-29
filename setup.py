#!/usr/bin/env python
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
########################################################################
# Copyright 2014 Matthieu Gaignière                matthieu@lightcode.fr
########################################################################
# This file is part of OVM.                          http://lightcode.fr
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
from distutils.core import setup
import shutil

setup(
    name='OVM',
    version='1.0',
    description='Open Virtualization Manager',
    author='Matthieu Gaigniere',
    author_email='matthieu@lightcode.fr',
    url='http://lightcode.fr',
    packages=[
        'ovm', 'ovm.vmcreation', 'ovm.vmmanagement', 'ovm.utils',
        'ovm.drivers', 'ovm.drivers.network', 'ovm.drivers.storage',
        'pyvirt'
    ],
    scripts=['bin/vm'],
    data_files=[
        ('/etc/bash_completion.d', ['bin/vm-completion'])
    ]
)

if os.path.exists('/etc/ovm'):
    print "Don't change /etc/ovm"
else:
    shutil.copytree('etc/', '/etc/ovm')