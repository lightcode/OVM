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
        xml = ET.tostring(self._root).decode('utf8')
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

    def get_os_info(self):
        # os-type : linux/windows/bsd/...
        # os-name : Debian/Windows/CentOS/...
        # os-version : text version of the OS
        info = {'os_type': None, 'os_name': None, 'os_version': None}
        try:
            tag = self._get_value('os_info')
        except Exception:
            return info
        else:
            if tag is None:
                return info

            if 'os_type' in tag.attrib:
                info['os_type'] = tag.attrib['os_type']
            if 'os_name' in tag.attrib:
                info['os_name'] = tag.attrib['os_name']
            if 'os_version' in tag.attrib:
                info['os_version'] = tag.attrib['os_version']
        return info

    def get_os_string(self):
        info = self.get_os_info()
        if info['os_name'] is None:
            return

        string = info['os_name']
        if info['os_version'] is not None:
            string += ' ' + info['os_version']

        return string

    def get_backup_state(self):
        try:
            bck = self._get_value('backup').attrib['state']
        except Exception:
            bck = 'off'
        return bck == 'on'

    def get_ip_address(self):
        try:
            ip_address = self._get_value('ip').attrib['address']
        except Exception:
            ip_address = None
        return ip_address
