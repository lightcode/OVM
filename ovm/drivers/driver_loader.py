#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import inspect

from ovm.exceptions import OVMError
from ovm.drivers.storage.generic import StorageDriver
from ovm.drivers.network.generic import NetworkDriver


class DriverLoader:
    STORAGE, NETWORK = 0, 1
    module_map = ("storage", "network")
    parent_class_map = (StorageDriver, NetworkDriver)

    def __init__(self, resource_type):
        module_name = self.module_map[resource_type]
        self.parent_class = self.parent_class_map[resource_type]
        self.root_module = ".".join(["ovm", "drivers", module_name])

    def load(self, driver_name):
        module_name = ".".join((self.root_module, driver_name.lower()))

        try:
            pkg = importlib.import_module(module_name)
        except ImportError:
            raise OVMError('No driver "{0}" found.'.format(driver_name))

        clsmembers = inspect.getmembers(pkg, inspect.isclass)

        for _, classobj in clsmembers:
            if classobj is self.parent_class:
                continue

            if issubclass(classobj, self.parent_class):
                return classobj
