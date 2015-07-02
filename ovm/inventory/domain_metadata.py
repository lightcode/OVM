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


import xml.etree.ElementTree as ET

import libvirt


class DomainMetadata(object):

    def __init__(self, domain):
        self._metadata = {}
        self._domain = domain

        try:
            xml = domain.metadata(
                libvirt.VIR_DOMAIN_METADATA_ELEMENT,
                'uri://ovm',
                libvirt.VIR_DOMAIN_XML_INACTIVE
            )
        except libvirt.libvirtError:
            pass
        else:
            root = ET.fromstring(xml)
            for element in root.findall('entry'):
                name = element.get('name')
                value = element.get('value')
                if name is not None:
                    self._metadata[name] = value

    def __iter__(self):
        for name, value in self._metadata.items():
            yield (name, value)

    def __getitem__(self, key):
        return self._metadata.get(str(key).lower())

    def __setitem__(self, key, value):
        self._metadata[str(key).lower()] = str(value)
        self.save()

    def get(self, name):
        return self._metadata.get(str(name).lower())

    def update(self, entries=None, **kargs):
        if type(entries) is dict:
            kargs.update(entries)

        for name, value in kargs.items():
            name = str(name).lower()
            self._metadata[name] = str(value)
        self.save()

    def save(self):
        root = ET.Element('metadata')

        for name, value in self._metadata.items():
            entry = ET.SubElement(root, 'entry')
            entry.set('name', name)
            entry.set('value', value)

        xml = ET.tostring(root).decode('utf8')
        self._domain.setMetadata(
            libvirt.VIR_DOMAIN_METADATA_ELEMENT,
            xml,
            'ovm',
            'uri://ovm',
            libvirt.VIR_DOMAIN_XML_INACTIVE
        )
