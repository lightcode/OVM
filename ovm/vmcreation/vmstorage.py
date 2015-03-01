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


import os

from lxml import etree

from ovm.utils.copyfile import CopyFile
from ovm.libvirt.libvirtconn import LibvirtConn


class VMStorage(object):
    def __init__(self, driver, **params):
        self._template = None
        self._vmd = None
        self._driver = driver()
        self._params = params
        self._driver.set_params(**params)

    def set_vmd(self, vmd):
        self._vmd = vmd
        self._driver.set_volume_name('%s-main.qcow2' % vmd.name())

    def pool_name(self):
        return self._params.get('pool_name')

    def set_size(self, size):
        self._params['image_size'] = int(size)

    def import_template(self, template):
        self._template = template
        main_disk = template._config['main_disk']
        self._driver.set_params(**main_disk)
        self._driver.set_params(driver_name='qemu')

    def create_disk(self, template):
        # 1. Find the pool path
        vol_name = self._driver._volume_name
        pool = LibvirtConn._conn.storagePoolLookupByName(self.pool_name())
        xml = pool.XMLDesc()
        pool_xml = etree.fromstring(xml)
        path_xml = pool_xml.xpath('/pool/target/path')[0]
        pool_path = path_xml.text
        img_target = os.path.join(pool_path, vol_name)

        # 2. Add volume into the pool
        xml = self._driver._get_vol_xml()
        vol = pool.createXML(xml.decode('utf8'))

        # 3. Copy template image in new pool
        img_path = template.get_path()
        cf = CopyFile('Copying image')
        cf.copy_progress(img_path, img_target)

        pool.refresh()
        vol = pool.storageVolLookupByName(vol_name)

        # 4. Resize if new size specified
        if 'image_size' in self._params:
            newsize = self._params['image_size']
            vol.resize(newsize * (1024 ** 3))

        return img_target

    def get_xml(self):
        return self._driver.get_disk_xml()
