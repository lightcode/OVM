#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
from distutils import spawn

from ovm.utils.compat23 import etree
from ovm.configuration import Configuration
from ovm.exceptions import OVMError


class DomainDefinition:
    def __init__(self, template, name):
        self.name = name
        self._template = template
        self._network = None
        self._storage = None
        self._devices = []

        self._vcpu = self._template.vcpu
        self._memory = self._template.memory
        self._main_disk = None

    @staticmethod
    def find_kvm():
        commands = ("qemu-kvm", "kvm")
        for command in commands:
            path = spawn.find_executable(command)
            if path:
                return path

        # Patch for CentOS 7
        path = "/usr/libexec/qemu-kvm"
        if os.path.isfile(path):
            return path
        raise OVMError("Path to KVM no found.")

    def network(self):
        return self._network

    def set_network(self, network):
        self._network = network

    def storage(self):
        return self._storage

    def set_storage(self, storage):
        self._storage = storage

    @property
    def vcpu(self):
        return self._vcpu

    @vcpu.setter
    def vcpu(self, vcpu):
        self._vcpu = int(vcpu)

    @property
    def memory(self):
        return self._memory

    @memory.setter
    def memory(self, memory):
        self._memory = int(memory)

    def _get_basevm(self):
        basename = "base-vm.xml"
        basevm_path = os.path.join(Configuration.ETC, basename)
        try:
            with open(basevm_path) as fd:
                tree = etree.parse(fd)
        except OSError as e:
            raise OVMError("Cannot open {}: {}".format(basename, e))

        root = tree.getroot()

        devices = root.find("devices")
        for emulator in devices.findall("emulator"):
            devices.remove(emulator)

        emulator = etree.SubElement(devices, "emulator")
        emulator.text = self.find_kvm()

        return root

    def create_main_disk(self):
        name = "{}-main".format(self.name)
        disk = self._storage.create_disk(name, self._template.main_disk)
        self._devices.append(disk.xml_definition)
        self._main_disk = disk
        return disk.path

    def resize_main_disk(self, new_size):
        self._main_disk.resize(new_size)

    def create_main_network_interface(self):
        netdef = self._network.create_interface(self._template.main_interface)
        self._devices.append(netdef)

    def get_xml(self):
        domain = self._get_basevm()

        # Add VM params
        name = etree.SubElement(domain, "name")
        name.text = str(self.name)
        memory = etree.SubElement(domain, "memory")
        memory.text = str(self.memory)
        memory.attrib["unit"] = "MiB"
        vcpu = etree.SubElement(domain, "vcpu")
        vcpu.text = str(self.vcpu)

        devices = domain.find("devices")

        for device_xml in self._devices:
            node = etree.fromstring(device_xml)
            devices.append(node)

        return etree.tostring(domain)
