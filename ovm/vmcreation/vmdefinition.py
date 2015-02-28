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


import os.path
from ovm.app import App
from lxml import etree


class VMDefinition(object):
    def __init__(self, template, name):
        self._name = name
        self._template = template
        self._network = None
        self._storage = None
        self._vcpu = 1
        self._memory = 256

        default_vcpu = self._template.get_default_vcpu()
        if default_vcpu:
            self._vcpu = default_vcpu

        default_memory = self._template.get_default_memory()
        if default_memory:
            self._memory = default_memory

    def name(self):
        return self._name

    def network(self):
        return self._network

    def set_network(self, network):
        self._network = network

    def storage(self):
        return self._storage

    def set_storage(self, storage):
        self._storage = storage

    def vcpu(self):
        return self._vcpu

    def set_vcpu(self, vcpu):
        self._vcpu = vcpu

    def memory(self):
        return self._memory

    def set_memory(self, memory):
        self._memory = int(memory)

    def _get_basevm(self):
        basevm_path = os.path.join(App.ETC, 'base-vm.xml')
        try:
            with open(basevm_path) as file_:
                tree = etree.parse(file_)
        except Exception as e:
            App.fatal('Cannot open base-vm.xml: %s' % str(e))
        else:
            return tree.getroot()

    def get_xml(self):
        root = self._get_basevm()
        domain = root

        # Add VM params
        name = etree.SubElement(domain, 'name')
        name.text = self.name()
        memory = etree.SubElement(domain, 'memory')
        memory.text = str(self.memory())
        memory.attrib['unit'] = 'MiB'
        vcpu = etree.SubElement(domain, 'vcpu')
        vcpu.text = str(self.vcpu())

        devices = root.find('devices')

        # Add network in device
        net = etree.fromstring(self.network().get_xml())
        devices.append(net)

        # Add storage in device
        storage_xml = etree.fromstring(self.storage().get_xml())
        devices.append(storage_xml)

        return etree.tostring(root)
