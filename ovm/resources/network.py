#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ovm.utils.compat23 import etree
from ovm.exceptions import OVMError
from ovm.inventory.ip_allocation import IpAllocation


ALLOCATION_STATIC, ALLOCATION_DHCP = 0, 1


class Network:
    def __init__(self, name, driver, ipv4_pool=None, **params):
        self.name = name
        self.ipv4_pool = ipv4_pool

        # Parse and check method
        method = params.get("ipv4_allocation", "dhcp")
        map_text_const = dict(dhcp=ALLOCATION_DHCP, static=ALLOCATION_STATIC)
        try:
            self.allocation_method = map_text_const[method]
        except KeyError:
            raise OVMError(
                'error with network "{}": unknown ' '"ipv4_allocation" value.'.format(
                    self.name
                )
            )

        # Set drivers and its configuration
        self._driver = driver()
        self._driver.set_params(**params)

    def new_ipv4_allocation(self):
        return IpAllocation(self)

    def create_interface(self, template_params):
        self._driver.set_params(driver_type=template_params["model"])
        netdef = self._driver.generate_xml()
        return etree.tostring(netdef).decode("utf-8")
