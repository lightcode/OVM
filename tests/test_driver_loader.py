#!/usr/bin/env python3

import unittest

from ovm.drivers.driver_loader import DriverLoader
from ovm.drivers.storage.lvm import LvmDriver
from ovm.drivers.storage.file import FileDriver
from ovm.drivers.network.openvswitch import OpenvSwitchDriver


class TestDriverLoader(unittest.TestCase):

    def test_to_load_lvm_driver(self):
        """this should return the lvm driver"""
        dl = DriverLoader(DriverLoader.STORAGE)
        driver = dl.load('lvm')
        self.assertEqual(driver, LvmDriver)

    def test_to_load_file_driver(self):
        """this should return the file driver"""
        dl = DriverLoader(DriverLoader.STORAGE)
        driver = dl.load('file')
        self.assertEqual(driver, FileDriver)

    def test_to_load_openvswitch_driver(self):
        """this should return the openvswitch driver"""
        dl = DriverLoader(DriverLoader.NETWORK)
        driver = dl.load('openvswitch')
        self.assertEqual(driver, OpenvSwitchDriver)

    def test_to_load_non_existing_driver(self):
        """this should raise a ValueError"""
        dl = DriverLoader(DriverLoader.NETWORK)
        self.assertRaises(ValueError, dl.load, 'non-existing-driver')
