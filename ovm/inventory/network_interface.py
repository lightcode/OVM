#!/usr/bin/env python3


class NetworkInterface:
    def __init__(self, xmldesc):
        self.xmldesc = xmldesc

    def get_network_name(self):
        source = self.xmldesc.xpath('source')[0]
        return source.attrib.get('network')

    def get_portgroup(self):
        source = self.xmldesc.xpath('source')[0]
        return source.attrib.get('portgroup')

    def get_mac(self):
        try:
            mac_xml = self.xmldesc.xpath('mac')[0]
        except:
            return
        else:
            return mac_xml.attrib.get('address')
