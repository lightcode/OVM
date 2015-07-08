#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
########################################################################
# Copyright 2015 Matthieu Gaignière                  http://lightcode.fr
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

from ovm.exceptions import OVMError
from ovm.drivers.driver_loader import DriverLoader
from ovm.resources.network import Network
from ovm.resources.storage_pool import StoragePool


class Resources:

    resources = None
    _cache = {}

    @classmethod
    def __init__(cls, path):
        try:
            with open(path) as fd:
                cls.resources = yaml.load(fd)
        except OSError:
            raise OVMError(
                'Cannot access to resources configuration file.')

    @classmethod
    def get_resources_ty_type(cls, resource_type):
        map_vars = {
            'storage': (DriverLoader.STORAGE, StoragePool),
            'networks': (DriverLoader.NETWORK, Network)
        }

        resource_var = map_vars[resource_type]
        driver_loader_type = resource_var[0]
        resource_class = resource_var[1]

        if resource_type in cls._cache:
            return cls._cache[resource_type]

        resources_list = []

        dl = DriverLoader(driver_loader_type)
        for name, options in cls.resources[resource_type].items():
            driver_name = options.pop('driver')
            driver = dl.load(driver_name)
            resources_list.append(resource_class(name, driver, **options))

        cls._cache[resource_type] = resources_list
        return resources_list

    @classmethod
    def get_networks(cls):
        return cls.get_resources_ty_type('networks')

    @classmethod
    def get_storage_pools(cls):
        return cls.get_resources_ty_type('storage')

    @classmethod
    def get_storage_pool(cls, name):
        for storage in cls.get_storage_pools():
            if storage.name == name:
                return storage
        raise OVMError(
            'Cannot find storage pool named "{0}".'.format(name))

    @classmethod
    def get_network(cls, name):
        for network in cls.get_networks():
            if network.name == name:
                return network
        raise OVMError('Cannot find network named "{0}".'.format(name))
