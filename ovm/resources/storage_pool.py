#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ovm.inventory.disk import Disk


class StoragePool:
    def __init__(self, name, driver, **params):
        self._params = params
        self.root = params.get("root")
        self.name = name

        self.driver = driver()
        self.driver.set_params(**params)

    def create_disk(self, name, params):
        device = Disk(storage_pool=self, name=name, template_params=params)
        return device
