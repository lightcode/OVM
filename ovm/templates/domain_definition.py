#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
from lxml import etree

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
        basename = 'base-vm.xml'
        basevm_path = os.path.join(Configuration.ETC, basename)
        try:
            with open(basevm_path) as fd:
                tree = etree.parse(fd)
        except OSError as e:
            raise OVMError('Cannot open {}: {}'.format(basename, e))
        else:
            return tree.getroot()

    def create_main_disk(self):
        name = '{}-main'.format(self.name)
        disk = self._storage.create_disk(name, self._template.main_disk)
        self._devices.append(disk.xml_definition)
        self._main_disk = disk
        return disk.path

    def resize_main_disk(self, new_size):
        self._main_disk.resize(new_size)

    def get_xml(self):
        root = self._get_basevm()
        domain = root

        # Add VM params
        name = etree.SubElement(domain, 'name')
        name.text = str(self.name)
        memory = etree.SubElement(domain, 'memory')
        memory.text = str(self.memory)
        memory.attrib['unit'] = 'MiB'
        vcpu = etree.SubElement(domain, 'vcpu')
        vcpu.text = str(self.vcpu)

        devices = root.find('devices')

        # Add network in device
        net = etree.fromstring(self.network().get_xml())
        devices.append(net)

        for device_xml in self._devices:
            node = etree.fromstring(device_xml)
            devices.append(node)

        return etree.tostring(root)
