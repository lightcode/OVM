#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import unittest

from ovm.configuration import Configuration
from ovm.resources.resources import Resources


ROOT = os.path.dirname(os.path.realpath(__file__))
CONFIG = os.path.join(ROOT, "files", "resources.yml")

Configuration.IP_DATABASE = os.path.join(ROOT, "files", "ipdatabase.db")
Resources(CONFIG)


class TestIpAllocation(unittest.TestCase):
    def test_to_get_new_ip_twice(self):
        """should return two differents ips"""
        network = Resources.get_network("labs")

        alloc1 = network.new_ipv4_allocation()
        alloc1.hold_ip("domtest")

        alloc2 = network.new_ipv4_allocation()
        alloc2.hold_ip("domtest")
        self.assertNotEqual(alloc1.address, alloc2.address)

    def test_to_release_an_allocation(self):
        """should delete the ip address from the database and allocate it
        a second time"""
        network = Resources.get_network("labs")

        alloc = network.new_ipv4_allocation()
        alloc.release_ips("domtest")

        alloc1 = network.new_ipv4_allocation()
        alloc1.hold_ip("domtest")

        alloc = network.new_ipv4_allocation()
        alloc.release_ips("domtest")

        alloc2 = network.new_ipv4_allocation()
        alloc2.hold_ip("domtest")

        self.assertEqual(alloc1.address, alloc2.address)
