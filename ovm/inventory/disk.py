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


from lxml import etree

from ovm.exceptions import OVMError


class Disk:

    def __init__(self, **kargs):
        self.guest_dev = None

        if 'xmldef' in kargs:
            xmldef = kargs['xmldef']

            disk_type = xmldef.attrib.get('type')
            if disk_type not in ('file', 'block'):
                raise OVMError('Unknown disk type.')

            source = xmldef.find('source')
            if source is None:
                raise OVMError('Source is missing on the libvirt device.')

            disk_path_attr = dict(file='file', block='dev').get(disk_type)
            disk_path = source.attrib.get(disk_path_attr)

            target = xmldef.find('target')
            if target is not None:
                self.guest_dev = str(target.attrib.get('dev'))

            from ovm.resources.resources import Resources
            storage_pool = None
            for storage in Resources.get_storage_pools():
                if disk_path.startswith(storage.root):
                    storage_pool = storage
                    break

            if storage_pool is None:
                raise OVMError('Cannot find storage pool.')

            driver = storage_pool.driver

        elif 'storage_pool' in kargs and 'name' in kargs:
            storage_pool = kargs['storage_pool']
            driver = storage_pool.driver

            template_params = kargs.get('template_params', dict())
            name = str(kargs['name'])
            image = template_params.get('image')
            self._template_params = template_params
            disk_path = driver.import_image(image, name)

        else:
            raise OVMError('Not enough arguments are passed to Disk.')

        self.path = disk_path
        self.pool = storage_pool
        self._driver = driver

    @property
    def xml_definition(self):
        if not self._template_params:
            raise NotImplementedError(
                'Cannot get xml definition without creation')

        target = etree.Element('target')
        target.attrib['dev'] = self._template_params.get('target_dev')
        target.attrib['bus'] = self._template_params.get('target_bus')
        xmldef = self._driver.generate_xml(self)
        xmldef.append(target)

        return etree.tostring(xmldef).decode('utf-8')

    def resize(self, new_size):
        self._driver.resize_disk(self, new_size)

    def remove(self):
        self._driver.remove_disk(self)

    @property
    def size(self):
        return self._driver.disk_real_size(self)
