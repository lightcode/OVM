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
from lxml.builder import E

from ovm.drivers import DriverError
from ovm.drivers.storage.generic import StorageDriver


__all__ = ['FileDriver']


class FileDriver(StorageDriver):

    def __init__(self):
        super(FileDriver, self).__init__()
        self._params = {'disk_format': 'qcow2'}

    def set_params(self, **params):
        if 'disk_format' in params:
            disk_format = str(params['disk_format'])
            if disk_format not in ('raw', 'qcow2'):
                raise DriverError('Disk format not supported')
            params['disk_format'] = disk_format

        super(FileDriver, self).set_params(**params)

    def generate_xml(self, disk):
        xmldef = (
            E.disk(
                E.driver(
                    name='qemu',
                    type=self._params['disk_format'],
                    cache='writeback'
                ),
                E.source(
                    file=disk.path
                ),
                type='file',
                device='disk'
            )
        )
        return xmldef

    def resize_disk(self, disk, new_size):
        if not os.path.exists(disk.path):
            raise DriverError('Path "{0}" does not exists'.format(disk.path))

        args = ['qemu-img', 'resize', disk.path, '{}G'.format(new_size)]
        with Popen(args, stdout=PIPE, stderr=PIPE) as process:
            process.wait()
            if process.returncode != 0:
                print(process.stderr.read())

    def import_image(self, image, name):
        path = os.path.join(self._params.get('root'), name)
        try:
            fd = open(path, 'w+')
        finally:
            fd.close()
        image.copy_on_device(path, self._params['disk_format'])
        return path

    def remove_disk(self, disk):
        try:
            os.remove(disk.path)
        except OSError as err:
            print('Cannot remove disk "{}": {}'.format(disk.path, err))
        else:
            print('Disk "{}" removed'.format(disk.path))
