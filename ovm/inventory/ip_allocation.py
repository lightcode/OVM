#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

from ovm.configuration import Configuration
from ovm.exceptions import OVMError
from ovm.utils.logger import logger


def is_ipv4_valid(ip):
    try:
        ip = [i for i in map(int, ip.split(".", 3)) if 0 <= i <= 255]
    except ValueError:
        return False
    return len(ip) == 4


def iprange(a, b):
    if not is_ipv4_valid(a) or not is_ipv4_valid(b):
        raise ValueError("Bap IP address")
    a = int("".join(["{0:08b}".format(int(i)) for i in a.split(".")]), 2)
    b = int("".join(["{0:08b}".format(int(i)) for i in b.split(".")]), 2)
    if a > b:
        raise ValueError("Invalid range")
    for ip in range(a, b + 1):
        yield ".".join([str(ip >> (8 * i) & 255) for i in range(3, -1, -1)])


class IpAllocation:
    def __init__(self, network):
        self.address = None
        self.domain = None

        self._network = network
        if network:
            self.pool = network.ipv4_pool

        self._connection = self.get_connection()

    def __del__(self):
        if self._connection:
            self._connection.close()

    def _get_used_ips(self):
        cur = self._connection.cursor()
        cur.execute("SELECT address FROM ipv4 WHERE network=?", (self._network.name,))
        return [e[0] for e in cur.fetchall()]

    def get_allocations(self):
        cur = self._connection.cursor()
        cur.execute(
            "SELECT domain, address FROM ipv4 WHERE network=?", (self._network.name,)
        )
        for domain, address in cur:
            alloc = IpAllocation(self._network)
            alloc.address = address
            alloc.domain = domain
            yield alloc

    @staticmethod
    def remove_domain(domain):
        alloc = IpAllocation(None)
        cur = alloc._connection.cursor()
        cur.execute("DELETE FROM ipv4 WHERE domain=?", (domain,))
        alloc._connection.commit()

    def remove_allocation(self, address):
        cur = self._connection.cursor()
        cur.execute(
            "DELETE FROM ipv4 WHERE network=? AND address=?",
            (self._network.name, address),
        )
        self._connection.commit()

    @staticmethod
    def get_connection():
        logger.debug("Connect to the IP database (%s)", Configuration.IP_DATABASE)
        connection = sqlite3.connect(Configuration.IP_DATABASE)
        cur = connection.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS ipv4 "
            "(domain text, network text, address text)"
        )
        connection.commit()
        return connection

    def new_ip(self):
        used_ips = self._get_used_ips()
        ipstart = self.pool["ip_start"]
        ipend = self.pool["ip_end"]
        for ip in iprange(ipstart, ipend):
            if ip not in used_ips:
                return ip

        raise OVMError("No IPs available in your IP pool")

    def check_ip(self, address):
        if not is_ipv4_valid(address):
            raise OVMError('The IP address "{}" is not valid.'.format(address))

        if address not in iprange(self.pool["ip_start"], self.pool["ip_end"]):
            raise OVMError("This IP is not in " "the defined range".format(address))

        if address in self._get_used_ips():
            raise OVMError(
                'The IP address "{}" has ' "already been attributed".format(address)
            )

    def hold_ip(self, domain, address=None):
        if address:
            self.check_ip(address)
        else:
            address = self.new_ip()

        self.address = address

        cur = self._connection.cursor()
        cur.execute(
            "INSERT INTO ipv4(domain, network, address) VALUES(?,?,?)",
            (domain, self._network.name, self.address),
        )
        self._connection.commit()

        logger.debug("New allocation saved: %s -> %s", domain, self.address)

    def release_ips(self, domain):
        cur = self._connection.cursor()
        cur.execute(
            "DELETE FROM ipv4 WHERE network=? AND domain=?",
            (self._network.name, domain),
        )
        self._connection.commit()

        logger.debug('Release IP allocation for domain "%s"', domain)

    @staticmethod
    def flush_network(network):
        connection = IpAllocation.get_connection()
        cur = connection.cursor()
        cur.execute("DELETE FROM ipv4 WHERE network=?", (network,))
        connection.commit()
        connection.close()

    def remove(self):
        if not self.address:
            return

        cur = self._connection.cursor()
        cur.execute(
            "DELETE FROM ipv4 WHERE network=? AND address=?",
            (self._network.name, self.address),
        )
        self._connection.commit()

        logger.debug(
            'Realease IP "%s" from network "%s"', self.address, self._network.name
        )
