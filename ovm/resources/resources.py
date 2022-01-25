#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
            raise OVMError("Cannot access to resources configuration file.")

    @classmethod
    def get_resources_ty_type(cls, resource_type):
        map_vars = {
            "storage": (DriverLoader.STORAGE, StoragePool),
            "networks": (DriverLoader.NETWORK, Network),
        }

        resource_var = map_vars[resource_type]
        driver_loader_type = resource_var[0]
        resource_class = resource_var[1]

        if resource_type in cls._cache:
            return cls._cache[resource_type]

        resources_list = []

        dl = DriverLoader(driver_loader_type)
        resource = cls.resources[resource_type].copy()
        for name, options in resource.items():
            local_options = options.copy()
            driver_name = local_options.pop("driver")
            driver = dl.load(driver_name)
            resources_list.append(resource_class(name, driver, **local_options))

        cls._cache[resource_type] = resources_list
        return resources_list

    @classmethod
    def get_networks(cls):
        return cls.get_resources_ty_type("networks")

    @classmethod
    def get_storage_pools(cls):
        return cls.get_resources_ty_type("storage")

    @classmethod
    def get_storage_pool(cls, name):
        for storage in cls.get_storage_pools():
            if storage.name == name:
                return storage
        raise OVMError('Cannot find storage pool named "{0}".'.format(name))

    @classmethod
    def get_network(cls, name):
        for network in cls.get_networks():
            if network.name == name:
                return network
        raise OVMError('Cannot find network named "{0}".'.format(name))
