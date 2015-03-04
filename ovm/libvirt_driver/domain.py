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

import os

import libvirt
from ovm.libvirt_driver.virdomainmeta import virDomainMeta
from ovm.app import App


class Volume(object):
    def __init__(self, xmldesc, vir_vol):
        self.vir_vol = vir_vol
        self.xmldesc = xmldesc

    def get_name(self):
        return self.vir_vol.name()

    def get_capacity(self):
        try:
            return self.vir_vol.info()[1]
        except:
            return 0

    def get_allocation(self):
        try:
            return self.vir_vol.info()[2]
        except:
            return 0

    def get_pool_name(self):
        source = self.xmldesc.xpath('source')[0]
        return source.attrib.get('pool')


class Interface(object):
    def __init__(self, xmldesc, ips=None):
        self.xmldesc = xmldesc
        self._ips = ips

    def get_network_name(self):
        source = self.xmldesc.xpath('source')[0]
        return source.attrib.get('network')

    def get_portgroup(self):
        source = self.xmldesc.xpath('source')[0]
        return source.attrib.get('portgroup')

    def get_mac(self):
        try:
            mac_xml = self.xmldesc.xpath('mac')[0]
        except:
            return
        else:
            return mac_xml.attrib.get('address')


class Domain(object):
    STATES = {1: 'Running', 3: 'Paused', 5: 'Stopped'}

    def __init__(self, vir_domain, libvirt_conn=None):
        self.vir_domain = vir_domain

        if libvirt_conn:
            self._libvirt_conn = libvirt_conn
        else:
            self._libvirt_conn = libvirt.open()

        saved_desc = self.vir_domain.XMLDesc(libvirt.VIR_DOMAIN_XML_INACTIVE)
        self._saved_tree = etree.fromstring(saved_desc)
        lived_desc = self.vir_domain.XMLDesc()
        self._lived_tree = etree.fromstring(lived_desc)

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
            raise Exception('The VM "{0}" cannot be removed. \
                Delete snapshots first.'.format(self.get_name()))
            return False

        if self.vir_domain.isActive():
            self.vir_domain.destroy()

        for vol in self.get_volumes():
            vol.vir_vol.delete()

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
                port = None
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
        all_ips = {}
        interfaces = []
        xml_ifaces = self._saved_tree.xpath(
            "/domain/devices/interface[@type='network']")
        for iface in xml_ifaces:
            inter = Interface(iface)
            mac = inter.get_mac()
            if mac in all_ips:
                ips = all_ips[mac]
            else:
                ips = {'ipv4': None}
            interfaces.append(Interface(iface, ips=ips))
        return interfaces

    def get_volumes(self):
        volumes = []
        disks = self._saved_tree.xpath(
            "/domain/devices/disk[@device='disk']")
        for disk in disks:
            src = disk.xpath('source')[0]
            poolname = src.attrib.get('pool')
            volname = src.attrib.get('volume')
            if not poolname or not poolname:
                continue
            pool = self._libvirt_conn.storagePoolLookupByName(poolname)
            try:
                vol = pool.storageVolLookupByName(volname)
            except Exception:
                pass
            else:
                volumes.append(Volume(disk, vol))
        return volumes

    def get_backup_state(self):
        meta = virDomainMeta(self.vir_domain)
        state = meta.get_backup_state()
        return state

    def get_backup_text(self):
        state = self.get_backup_state()
        return 'On' if state else 'Off'

    def set_backup(self, state):
        meta = virDomainMeta(self.vir_domain)
        value = 'on' if state else 'off'
        meta.set_value('backup', 'state', value)

    def set_os_type(self, os_type):
        meta = virDomainMeta(self.vir_domain)
        if os_type is not None:
            meta.set_value('os_info', 'os_type', str(os_type))

    def set_os_name(self, os_name):
        meta = virDomainMeta(self.vir_domain)
        if os_name is not None:
            meta.set_value('os_info', 'os_name', str(os_name))

    def set_os_version(self, os_version):
        meta = virDomainMeta(self.vir_domain)
        if os_version is not None:
            meta.set_value('os_info', 'os_version', str(os_version))

    def get_os_info(self):
        meta = virDomainMeta(self.vir_domain)
        info = meta.get_os_info()
        return info

    def get_os_string(self):
        meta = virDomainMeta(self.vir_domain)
        string = meta.get_os_string()
        return string

    def set_main_ipv4(self, ip):
        meta = virDomainMeta(self.vir_domain)
        meta.set_value('ip', 'address', ip)

    def get_main_ipv4(self):
        meta = virDomainMeta(self.vir_domain)
        ipv4 = meta.get_ip_address()
        return ipv4
