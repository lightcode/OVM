#!/usr/bin/env python3

import libvirt

from ovm.inventory.domain import Domain
from ovm.utils.logger import logger


class Inventory:

    _conn = None
    _connection_string = 'qemu:///system'

    @classmethod
    def open(cls):
        cls._conn = libvirt.open(cls._connection_string)
        logger.debug('New connection to libvirt opened.')

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
