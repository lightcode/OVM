#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ovm.inventory.domain import Domain
from ovm.lvconnect import LibvirtConnect


class Inventory:
    @classmethod
    def get_domains(cls):
        connection = LibvirtConnect.get_connection()
        for domain in connection.listAllDomains():
            yield Domain(domain)

    @classmethod
    def get_domain(cls, name):
        connection = LibvirtConnect.get_connection()
        domain = connection.lookupByName(name)
        return Domain(domain)

    @classmethod
    def add_domain(cls, domain):
        connection = LibvirtConnect.get_connection()
        connection.defineXML(domain.get_xml().decode("utf8"))
