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


import libvirt

from ovm.inventory.domain import Domain


class Inventory:

    _conn = None
    _connection_string = 'qemu:///system'

    @classmethod
    def open(cls):
        cls._conn = libvirt.open(cls._connection_string)

    @classmethod
    def new_connection(cls):
        return libvirt.open(cls._connection_string)

    @classmethod
    def get_domains(cls):
        for domain in cls._conn.listAllDomains():
            yield Domain(domain)

    @classmethod
    def get_domain(cls, name):
        domain = cls._conn.lookupByName(name)
        return Domain(domain)

    @classmethod
    def add_domain(cls, domain):
        cls._conn.defineXML(domain.get_xml().decode('utf8'))
