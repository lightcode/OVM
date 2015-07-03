#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
########################################################################
# Copyright 2014 Matthieu Gaignière                  http://lightcode.fr
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


from lxml import etree
from lxml.builder import E

from ovm.drivers.storage.generic import StorageDriver


__all__ = ['VolumeDriver']


class VolumeDriver(StorageDriver):
    def __init__(self):
        super(VolumeDriver, self).__init__()
        self._volume_name = None

    def set_volume_name(self, name):
        self._volume_name = name

    def get_disk_xml(self):
        tree = (
            E.disk(
                E.driver(
                    name=self._params.get('driver_name'),
                    type=self._params.get('image_format'),
                    cache='writeback'
                ),
                E.source(
                    pool=self._params.get('pool_name'),
                    volume=self._volume_name
                ),
                E.target(
                    dev=self._params.get('image_dev'),
                    bus=self._params.get('image_bus')
                ),
                type='volume', device='disk'
            )
        )
        return etree.tostring(tree)

    ####################
    # DRIVER SPECIFIC
    ####################
    def _get_vol_xml(self):
        tree = (
            E.volume(
                E.name(self._volume_name),
                E.capacity(str(self._params.get('image_size'))),
                E.target(
                    E.format(type='qcow2')
                )
            )
        )
        return etree.tostring(tree)
