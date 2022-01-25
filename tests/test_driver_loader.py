#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from ovm.exceptions import OVMError
from ovm.drivers.driver_loader import DriverLoader
from ovm.drivers.storage.lvm import LvmDriver
from ovm.drivers.storage.file import FileDriver
from ovm.drivers.network.bridge import BridgeDriver


class TestDriverLoader(unittest.TestCase):
    def test_to_load_lvm_driver(self):
        """this should return the lvm driver"""
        dl = DriverLoader(DriverLoader.STORAGE)
        driver = dl.load("lvm")
        self.assertEqual(driver, LvmDriver)

    def test_to_load_file_driver(self):
        """this should return the file driver"""
        dl = DriverLoader(DriverLoader.STORAGE)
        driver = dl.load("file")
        self.assertEqual(driver, FileDriver)

    def test_to_load_openvswitch_driver(self):
        """this should return the openvswitch driver"""
        dl = DriverLoader(DriverLoader.NETWORK)
        driver = dl.load("bridge")
        self.assertEqual(driver, BridgeDriver)

    def test_to_load_non_existing_driver(self):
        """this should raise a OVMError"""
        dl = DriverLoader(DriverLoader.NETWORK)
        self.assertRaises(OVMError, dl.load, "non-existing-driver")
