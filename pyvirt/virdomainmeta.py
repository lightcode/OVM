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


import libvirt
import xml.etree.ElementTree as ET


def set_attrib(root, tag, name, value):
    elmt = None
    for child in root:
        if child.tag == tag:
            elmt = child

    if elmt is None:
        elmt = ET.Element(tag)
        root.append(elmt)

    elmt.attrib[name] = value


class virDomainMeta(object):
    def __init__(self, domain):
        try:
            xml = domain.metadata(
                libvirt.VIR_DOMAIN_METADATA_ELEMENT,
                'uri://vm',
                libvirt.VIR_DOMAIN_XML_INACTIVE
            )
        except libvirt.libvirtError:
            xml = '<params></params>'

        root = ET.fromstring(xml)
        if root.tag != 'params':
            xml = '<params></params>'
            root = ET.fromstring(xml)

        self._root = root
        self._domain = domain

    def _save_xml(self):
        xml = ET.tostring(self._root)
        self._domain.setMetadata(
            libvirt.VIR_DOMAIN_METADATA_ELEMENT,
            xml,
            'vm',
            'uri://vm',
            libvirt.VIR_DOMAIN_XML_INACTIVE
        )

    def set_value(self, tag, name, value):
        set_attrib(self._root, tag, name, value)
        self._save_xml()

    def _get_value(self, name):
        return self._root.find(name)

    def get_backup_state(self):
        try:
            bck = self._get_value('backup').attrib['state']
        except Exception as e:
            bck = 'off'
        return (bck == 'on')

    def get_ip_address(self):
        try:
            network = self._get_value('network').attrib['name']
        except Exception as e:
            network = None

        try:
            ip_address = self._get_value('ip').attrib['address']
        except Exception as e:
            ip_address = None
        return ip_address