#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class NetworkInterface:
    def __init__(self, xmldesc):
        # Get the bridge name
        source = xmldesc.find("source")
        self.bridge = source.attrib.get("bridge")

        # Get all vlans
        vlan = xmldesc.find("vlan")
        self.vlans = []

        for tag in vlan.findall("tag"):
            self.vlans.append(tag.attrib.get("id"))

        # Get mac address
        mac_xml = xmldesc.find("mac")
        self.mac = mac_xml.attrib.get("address")
