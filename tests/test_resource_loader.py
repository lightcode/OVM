#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import os

from ovm.exceptions import OVMError
from ovm.resources.resources import Resources


ROOT = os.path.dirname(os.path.realpath(__file__))
CONFIG = os.path.join(ROOT, "files", "resources.yml")


class TestResourceLoader(unittest.TestCase):
    def test_to_load_storage(self):
        """get_storage_pools should return 2 pools"""
        Resources(CONFIG)
        self.assertEqual(len(Resources.get_storage_pools()), 2)

    def test_to_load_storage_several_times(self):
        """get_storage_pools should return 2 pools"""
        Resources(CONFIG)
        Resources.get_storage_pools()
        self.assertEqual(len(Resources.get_storage_pools()), 2)

    def test_to_load_networks(self):
        """get_networks should return 3 networks"""
        Resources(CONFIG)
        self.assertEqual(len(Resources.get_networks()), 3)

    def test_to_load_a_storage_pool(self):
        """get_storage should return the good storage pool"""
        Resources(CONFIG)
        for name in ("file_storage", "lvm_storage"):
            pool = Resources.get_storage_pool(name)
            self.assertEqual(pool.name, name)

    def test_to_load_a_network(self):
        """get_storage should return the good network"""
        Resources(CONFIG)
        for name in ("prod-1", "labs"):
            network = Resources.get_network(name)
            self.assertEqual(network.name, name)

    def test_to_load_non_existing_driver(self):
        """this should raise an OVMError"""
        Resources(CONFIG)
        with self.assertRaises(OVMError):
            Resources.get_storage_pool("non-existing-pool")


if __name__ == "__main__":
    unittest.main()
