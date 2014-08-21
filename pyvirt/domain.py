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
import json
from lxml import etree
from subprocess import Popen, PIPE
from virdomainmeta import virDomainMeta


class Volume(object):
    def __init__(self, xmldesc, vir_vol):
        self.vir_vol = vir_vol
        self.xmldesc = xmldesc

    def get_name(self):
        return self.vir_vol.name()

    def get_capacity(self):
        return self.vir_vol.info()[1]

    def get_allocation(self):
        return self.vir_vol.info()[2]

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

    def get_ipv4(self):
        return self._ips['ipv4']


class Domain(object):
    STATES = {1: 'Running', 3: 'Paused', 5: 'Stopped'}

    def __init__(self, vir_domain, libvirt_conn=None):
        self.vir_domain = vir_domain

        if libvirt_conn:
            self._libvirt_conn = libvirt_conn
        else:
            self._libvirt_conn = libvirt.open()

        xml = self.vir_domain.XMLDesc()
        self._saved_tree = etree.fromstring(xml)

    def _get_libvirt_state(self):
        return self.vir_domain.state()[0]

    def _mem_extract_value(self, node):
        (mem, unit) = (0, 'KiB')
        try:
            unit = node.attrib['unit']
        except KeyError:
            pass
        if unit not in ('k', 'KiB'):
            print "WARNING: this unit of memory isn't recognize"
        mem = int(node.text) * (2**10)
        return mem

    def get_name(self):
        return self.vir_domain.name()
    
    def get_state_text(self):
        num = self._get_libvirt_state()
        try:
            return self.STATES[num]
        except KeyError:
            return 'Unknown (%d)' % num

    def get_vcpu_count(self):
        try:
            node = self._saved_tree.xpath('/domain/vcpu')[0]
        except:
            print "Cannot get the 'vcpu' element in XML."
            return

        return int(node.text)
    
    def get_vnc_info(self):
        vnc_infos = {
            'screen': None
        }
        try:
            node = self._saved_tree.xpath(
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

    def _ga_get_ips(self):
        # cmd = [
        #     'virsh', 'qemu-agent-command', self.get_name(), 
        #     '{"execute":"guest-network-get-interfaces"}'
        # ]
        # process = Popen(cmd, stdout=PIPE, stderr=PIPE)
        # res = process.stdout.read()
        # process.communicate()
        # try:
        #     ifaces = json.loads(res)['return']
        # except ValueError:
        #     return {}

        # r_iface = {}
        # for iface in ifaces:
        #     hwaddr = iface['hardware-address']
        #     if hwaddr == '00:00:00:00:00:00':
        #         continue
        #     ipv4 = None
        #     for ip in iface['ip-addresses']:
        #         if ip['ip-address-type'] == 'ipv4':
        #             ipv4 = ip['ip-address']
        #             break
        #     r_iface[hwaddr] = {'ipv4': ipv4}
        # return r_iface
        return {}

    def get_interfaces(self):
        all_ips = self._ga_get_ips()
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
            pool = self._libvirt_conn.storagePoolLookupByName(poolname)
            vol = pool.storageVolLookupByName(volname)
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

    def set_main_ipv4(self, ip):
        meta = virDomainMeta(self.vir_domain)
        meta.set_value('ip', 'address', ip)

    def get_main_ipv4(self):
        ipv4 = None
        for iface in self.get_interfaces():
            ipv4 = iface.get_ipv4()
            if ipv4:
                return ipv4

        meta = virDomainMeta(self.vir_domain)
        ipv4 = meta.get_ip_address()
        return ipv4