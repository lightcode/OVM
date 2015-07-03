#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
########################################################################
# Copyright 2014 Matthieu Gaignière                  http://lightcode.fr
########################################################################
# This file is part of OVM.
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


import yaml
import importlib

import ovm.drivers.network      # flake8: noqa
import ovm.drivers.storage      # flake8: noqa
from ovm.utils.singleton import Singleton
from ovm.resources.network import Network
from ovm.resources.storage_pool import StoragePool


def get_driver(driver_type, driver_name):
    module_name = driver_name.lower().replace('driver', '')
    pkg = importlib.import_module(
        'ovm.drivers.{}.{}'.format(driver_type, module_name))
    return pkg.__dict__[driver_name]


class Resources(Singleton):
    path = None
    networks = {}
    storage = {}

    @classmethod
    def init(cls, path):
        cls.path = path

    @classmethod
    def load_resources(cls):
        if not cls.networks or not cls.storage:
            with open(cls.path) as fd:
                resources = yaml.load(fd)

            for name, network in resources['networks'].items():
                driver_name = network.pop('driver')
                driver = get_driver('network', driver_name)
                cls.networks[name] = Network(driver, **network)

            for name, storage in resources['storage'].items():
                driver_name = storage.pop('driver')
                driver = get_driver('storage', driver_name)
                cls.storage[name] = StoragePool(name, driver, **storage)

    @classmethod
    def get_networks(cls):
        cls.load_resources()
        return cls.networks

    @classmethod
    def get_storage(cls):
        cls.load_resources()
        return cls.storage
