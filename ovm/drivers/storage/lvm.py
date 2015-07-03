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


import os.path
from subprocess import Popen, PIPE
from lxml import etree
from lxml.builder import E

from ovm.drivers.storage.generic import StorageDriver


__all__ = ['LvmDriver']


class LvmDriver(StorageDriver):

    def __init__(self, path=None):
        super(LvmDriver, self).__init__()

        self.path = path

        self.driver_name = 'qemu'
        self.driver_type = 'raw'

    def _create_logical_volume(self, name):
        image = self._params.get('image')
        size = '{}G'.format(image.size)
        vgname = self._params.get('volume_group')
        args = ['lvcreate', '--size', size, '--name', str(name), vgname]
        with Popen(args, stdout=PIPE, stderr=PIPE) as process:
            process.wait()
            if process.returncode != 0:
                print(process.stderr.read())

    def generate_xml(self):
        tree = (
            E.disk(
                E.driver(
                    name=self.driver_name,
                    type=self.driver_type,
                    cache='writeback'
                ),
                E.source(
                    dev=self.path
                ),
                E.target(
                    dev=self._params.get('target_dev'),
                    bus=self._params.get('target_bus')
                ),
                type='block',
                device='disk'
            )
        )
        return etree.tostring(tree).decode('utf-8')

    def resize_disk(self, new_size):
        args = ['lvresize', '--size', '{}G'.format(new_size), self.path]
        with Popen(args, stdout=PIPE, stderr=PIPE) as process:
            process.wait()
            if process.returncode != 0:
                print(process.stderr.read())

    def create_disk(self, name, image):
        path = os.path.join(self._params.get('root'), name)
        self.path = path
        self._create_logical_volume(name)
        image.copy_on_device(path, self.driver_type)

    def remove(self):
        args = ['lvremove', '--force', self.path]
        with Popen(args, stdout=PIPE, stderr=PIPE) as process:
            process.wait()
            if process.returncode != 0:
                print(process.stderr.read())

    @property
    def capacity(self):
        # TODO: implement that
        return 0

    @property
    def allocated(self):
        # TODO: implement that
        return 0
