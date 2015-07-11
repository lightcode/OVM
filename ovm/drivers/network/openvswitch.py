#!/usr/bin/env python3

from lxml import etree
from lxml.builder import E

from ovm.drivers.network.generic import NetworkDriver


__all__ = ['OpenvSwitchDriver']


class OpenvSwitchDriver(NetworkDriver):
    def get_xml(self):
        tree = (
            E.interface(
                E.source(
                    network=self._params.get('net_name')
                ),
                E.virtualport(type='openvswitch'),
                E.model(type=self._params.get('driver_type')),
                type='network'
            )
        )

        if 'net_portgroup' in self._params:
            portgroup = self._params['net_portgroup']
            source_attr = tree.xpath('/interface/source')[0].attrib
            source_attr['portgroup'] = portgroup

        return etree.tostring(tree)
