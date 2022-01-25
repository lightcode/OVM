#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import unittest

from ovm.configuration import Configuration
from ovm.resources.resources import Resources
from ovm.resources.network import ALLOCATION_STATIC, ALLOCATION_DHCP


ROOT = os.path.dirname(os.path.realpath(__file__))
CONFIG = os.path.join(ROOT, "files", "resources.yml")

Configuration.IP_DATABASE = os.path.join(ROOT, "files", "ipdatabase.db")
Resources(CONFIG)


class TestNetwork(unittest.TestCase):
    def test_network_method(self):
        network = Resources.get_network("labs")
        self.assertEqual(network.allocation_method, ALLOCATION_STATIC)

        network = Resources.get_network("prod-1")
        self.assertEqual(network.allocation_method, ALLOCATION_DHCP)
