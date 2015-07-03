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


import os
import libvirt
from lxml import etree

from ovm.inventory.domain_metadata import DomainMetadata
from ovm.app import App
from ovm.inventory.volume import Volume
from ovm.inventory.network_interface import NetworkInterface
from ovm.resources.resources import Resources


class DomainException(Exception):
    pass


class Domain(object):
    STATES = {1: 'Running', 3: 'Paused', 5: 'Stopped'}

    def __init__(self, vir_domain, libvirt_conn=None):
        self.vir_domain = vir_domain

        self._cached_metadata = None

        if libvirt_conn:
            self._libvirt_conn = libvirt_conn
        else:
            self._libvirt_conn = libvirt.open()

        saved_desc = self.vir_domain.XMLDesc(libvirt.VIR_DOMAIN_XML_INACTIVE)
        self._saved_tree = etree.fromstring(saved_desc)
        lived_desc = self.vir_domain.XMLDesc()
        self._lived_tree = etree.fromstring(lived_desc)

    @property
    def metadata(self):
        if not self._cached_metadata:
            self._cached_metadata = DomainMetadata(self.vir_domain)
        return self._cached_metadata

    def is_active(self):
        return self.vir_domain.isActive()

    def get_save_file(self):
        return os.path.join(App.SAVED_VMS, self.get_name())

    def remove_save(self):
        if self.is_saved():
            os.remove(self.get_save_file())

    def remove(self):
        # We cannot remove vm with snapshots
        snapshots = self.vir_domain.listAllSnapshots()
        if snapshots:
            raise DomainException('The VM "{0}" cannot be removed. \
                Delete snapshots first.'.format(self.get_name()))

        if self.vir_domain.isActive():
            self.vir_domain.destroy()

        for vol in self.get_volumes():
            vol.remove()

        self.remove_save()

        return self.vir_domain.undefine()

    def save(self):
        if not self.is_active():
            raise Exception('the VM must be active.')
        if self.is_saved():
            raise Exception('the file to save the VM already exists.')
        self.vir_domain.save(self.get_save_file())

    def restore(self):
        if self.is_active():
            raise Exception('the VM must be inactive.')

        if not self.is_saved():
            raise Exception('this VM has already been saved.')

        save_file = self.get_save_file()
        self._libvirt_conn.restore(save_file)
        self.remove_save()

    def _get_libvirt_state(self):
        return self.vir_domain.state()[0]

    def _mem_extract_value(self, node):
        (mem, unit) = (0, 'KiB')
        try:
            unit = node.attrib['unit']
        except KeyError:
            pass
        if unit not in ('k', 'KiB'):
            print("WARNING: this unit of memory isn't recognize")
        mem = int(node.text) * (2**10)
        return mem

    def get_name(self):
        return self.vir_domain.name()

    def is_saved(self):
        return os.path.exists(self.get_save_file())

    def start(self):
        if self.is_saved():
            self.restore()
        else:
            self.vir_domain.create()

    def get_state_text(self):
        num = self._get_libvirt_state()

        if num == 5 and self.is_saved():
            return 'Saved'

        try:
            return self.STATES[num]
        except KeyError:
            return 'Unknown (%d)' % num

    def get_vcpu_count(self):
        try:
            node = self._saved_tree.xpath('/domain/vcpu')[0]
        except:
            print("Cannot get the 'vcpu' element in XML.")
            return

        return int(node.text)

    def get_vnc_info(self):
        vnc_infos = {
            'screen': None
        }
        try:
            node = self._lived_tree.xpath(
                "/domain/devices/graphics[@type='vnc']")[0]
        except:
            return {}
        else:
            try:
                port = int(node.attrib.get('port'))
            except:
                pass
            else:
                if port >= 5900:
                    vnc_infos['screen'] = port - 5900
        return vnc_infos

    def get_autostart(self):
        return self.vir_domain.autostart()

    def set_autostart(self, boolean):
        self.vir_domain.setAutostart(bool(boolean))

    def get_memory(self):
        """Returns the max memory the domain can use."""
        node = self._saved_tree.xpath('/domain/memory')[0]
        mem = self._mem_extract_value(node)
        return mem

    def get_current_memory(self):
        node = self._saved_tree.xpath('/domain/currentMemory')[0]
        mem = self._mem_extract_value(node)
        return mem

    def get_interfaces(self):
        interfaces = []
        xml_ifaces = self._saved_tree.xpath(
            "/domain/devices/interface[@type='network']")
        for iface in xml_ifaces:
            interfaces.append(NetworkInterface(iface))
        return interfaces

    def get_volumes(self):
        volumes = []
        disks = self._saved_tree.xpath(
            "/domain/devices/disk[@device='disk']")
        for disk in disks:
            disk_type = disk.attrib.get('type')
            if disk.attrib.get('type') is None:
                continue

            diskpath = ''
            src = disk.xpath('source')[0]
            if disk_type == 'file':
                diskpath = src.attrib.get('file')
            elif disk_type == 'block':
                diskpath = src.attrib.get('dev')

            if not diskpath:
                continue

            target_dev = disk.xpath('target')[0].attrib.get('dev')

            for storage in Resources.get_storage().values():
                if diskpath.startswith(storage.root):
                    volumes.append(Volume(storage, diskpath, target_dev))
                    break

        return volumes

    def get_os_info(self):
        # os-type : linux/windows/bsd/...
        # os-name : Debian/Windows/CentOS/...
        # os-version : text version of the OS

        info = {
            'os_type': self.metadata.get('os_type'),
            'os_name': self.metadata.get('os_name'),
            'os_version': self.metadata.get('os_version')
        }

        return info

    def get_os_string(self):
        info = self.get_os_info()
        if info['os_name'] is None:
            return

        string = info['os_name']
        if info['os_version'] is not None:
            string += ' ' + info['os_version']

        return string

    def set_main_ipv4(self, ip):
        self.metadata.update(ipv4_addr=ip)

    def get_main_ipv4(self):
        return self.metadata.get('ipv4_addr')
