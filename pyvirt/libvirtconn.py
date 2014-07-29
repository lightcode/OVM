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
from pyvirt.domain import Domain

class Singleton(object):
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance


class LibvirtConn(Singleton):
    @classmethod
    def open(cls):
        cls._conn = libvirt.open()

    @classmethod
    def get_domains(cls):
        for domain in cls._conn.listAllDomains():
            yield Domain(domain)

    @classmethod
    def get_domain(cls, name):
        domain = cls._conn.lookupByName(name)
        return Domain(domain)

    @classmethod
    def define_domain(cls, xml):
        cls._conn.defineXML(xml)
