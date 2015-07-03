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
from subprocess import Popen
from lxml import etree
from lxml.builder import E

from ovm.drivers.storage.generic import StorageDriver
from ovm.utils.copyfile import CopyFile


__all__ = ['FileDriver']


class FileDriver(StorageDriver):

    def __init__(self, path=None):
        super(FileDriver, self).__init__()

        self.path = path

    def generate_xml(self):
        tree = (
            E.disk(
                E.driver(
                    name=self._params.get('driver_name'),
                    type=self._params.get('image_format'),
                    cache='writeback'
                ),
                E.source(
                    file=self.path
                ),
                E.target(
                    dev=self._params.get('image_dev'),
                    bus=self._params.get('image_bus')
                ),
                type='file',
                device='disk'
            )
        )
        return etree.tostring(tree).decode('utf-8')

    def _copy_image(self, destination):
        source = self._params.get('path')
        cf = CopyFile('Copying image')
        cf.copy_progress(source, destination)

    def resize_disk(self, new_size):
        args = ['qemu-img', 'resize', self.path, '{}G'.format(new_size)]
        process = Popen(args)
        process.wait()

    def create_disk(self, name):
        path = os.path.join(self._params.get('root'), name)
        self.path = path
        self._copy_image(path)

    def remove(self):
        try:
            os.remove(self.path)
        except OSError as err:
            print('Cannot remove disk "{}": {}'.format(self.path, err))
        else:
            print('Disk "{}" removed'.format(self.path))

    @property
    def capacity(self):
        # TODO: implement that
        return 0

    @property
    def allocated(self):
        # TODO: implement that
        return 0
