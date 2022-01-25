#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ovm.utils.compat23 import etree
from ovm.drivers.network.generic import NetworkDriver


__all__ = ["BridgeDriver"]


class BridgeDriver(NetworkDriver):
    def generate_xml(self):
        interface = etree.Element("interface")
        interface.set("type", "bridge")

        source = etree.SubElement(interface, "source")
        source.set("bridge", self._params.get("bridge"))

        model = etree.SubElement(interface, "model")
        model.set("type", self._params.get("driver_type"))

        if self._params.get("openvswitch", False):
            virtualport = etree.SubElement(interface, "virtualport")
            virtualport.set("type", "openvswitch")

        if "vlan" in self._params:
            vlan_list = self._params.get("vlan")

            if not isinstance(vlan_list, list):
                vlan_list = [vlan_list]

            vlan = etree.SubElement(interface, "vlan")

            if len(vlan_list) > 1:
                vlan.set("trunk", "yes")

            for vlan_id in vlan_list:
                tag = etree.SubElement(vlan, "tag")
                tag.set("id", str(int(vlan_id)))

        return interface
