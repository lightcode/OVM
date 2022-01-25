#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import libvirt

from ovm.configuration import Configuration
from ovm.exceptions import DomainException, DriverError
from ovm.inventory.disk import Disk
from ovm.inventory.domain_metadata import DomainMetadata
from ovm.inventory.ip_allocation import IpAllocation
from ovm.inventory.network_interface import NetworkInterface
from ovm.lvconnect import LibvirtConnect
from ovm.utils.compat23 import etree
from ovm.utils.logger import logger


class Domain:
    STATES = {1: "Running", 3: "Paused", 5: "Stopped"}

    def __init__(self, vir_domain):
        self.vir_domain = vir_domain
        self._cached_metadata = None
        self._libvirt_conn = LibvirtConnect.get_connection()

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
        return os.path.join(Configuration.SAVED_VMS, self.get_name())

    def remove_save(self):
        if self.is_saved():
            os.remove(self.get_save_file())

    def remove(self):
        # We cannot remove vm with snapshots
        snapshots = self.vir_domain.listAllSnapshots()
        if snapshots:
            raise DomainException(
                'The VM "{0}" cannot be removed. \
                Delete snapshots first.'.format(self.get_name())
            )

        if self.vir_domain.isActive():
            self.vir_domain.destroy()

        for disk in self.get_disks():
            try:
                disk.remove()
            except DriverError as e:
                logger.warning(e)

        IpAllocation.remove_domain(self.get_name())

        self.remove_save()

        return self.vir_domain.undefine()

    def save(self):
        if not self.is_active():
            raise DomainException("the VM must be active.")
        if self.is_saved():
            raise DomainException("the file to save the VM already exists.")
        try:
            self.vir_domain.save(self.get_save_file())
        except libvirt.libvirtError as e:
            raise DomainException("libvirt returns an error: {0}".format(e))

    def restore(self):
        if self.is_active():
            raise DomainException("the VM must be inactive.")

        if not self.is_saved():
            raise DomainException("this VM has already been saved.")

        save_file = self.get_save_file()

        try:
            self._libvirt_conn.restore(save_file)
        except libvirt.libvirtError as e:
            raise DomainException("libvirt returns an error: {0}".format(e))

        self.remove_save()

    def _get_libvirt_state(self):
        return self.vir_domain.state()[0]

    def _mem_extract_value(self, node):
        (mem, unit) = (0, "KiB")
        try:
            unit = node.attrib["unit"]
        except KeyError:
            pass
        if unit not in ("k", "KiB"):
            logger.warning("WARNING: this unit of memory isn't recognize")
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
            return "Saved"

        try:
            return self.STATES[num]
        except KeyError:
            return "Unknown (%d)" % num

    def get_vcpu_count(self):
        vcpu = self._saved_tree.find("vcpu")
        return int(vcpu.text)

    def get_vnc_info(self):
        vncport = None

        devices = list(self.find_device("graphics", type="vnc"))

        if devices > 0:
            vncport = devices[0].attrib.get("port")

        if vncport is not None:
            vncport = int(vncport)

        if vncport < 0:
            vncport = None

        return dict(port=vncport)

    def get_autostart(self):
        return self.vir_domain.autostart()

    def set_autostart(self, boolean):
        self.vir_domain.setAutostart(bool(boolean))

    def get_memory(self):
        memory = self._saved_tree.find("memory")
        return self._mem_extract_value(memory)

    def get_current_memory(self):
        memory = self._saved_tree.find("currentMemory")
        return self._mem_extract_value(memory)

    def find_device(self, name, **kargs):
        devices = self._lived_tree.find("devices")

        def check_properties(device, properties):
            for key, value in properties:
                if device.attrib.get(key) != value:
                    return False
            return True

        for device in devices:
            if device.tag == name:
                if check_properties(device, kargs.items()):
                    yield device

    def get_interfaces(self):
        interfaces = []
        for iface in self.find_device("interface", type="bridge"):
            interfaces.append(NetworkInterface(iface))
        return interfaces

    def get_disks(self):
        disks = []
        for disk in self.find_device("disk", device="disk"):
            disks.append(Disk(xmldef=disk))
        return disks

    def get_os_info(self):
        # os-type : linux/windows/bsd/...
        # os-name : Debian/Windows/CentOS/...
        # os-version : text version of the OS

        info = {
            "os_type": self.metadata.get("os_type"),
            "os_name": self.metadata.get("os_name"),
            "os_version": self.metadata.get("os_version"),
        }

        return info

    def get_os_string(self):
        info = self.get_os_info()
        if info["os_name"] is None:
            return

        string = info["os_name"]
        if info["os_version"] is not None:
            string += " " + info["os_version"]

        return string

    def set_main_ipv4(self, ip):
        self.metadata.update(ipv4_addr=ip)

    def get_main_ipv4(self):
        return self.metadata.get("ipv4_addr")
