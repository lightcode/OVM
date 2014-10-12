#!/usr/bin/python3

########################################################################
#  Don't modify this part

import os
import sys
from ovm.drivers.storage.volume import VolumeDriver
from ovm.drivers.network.openvswitch import OpenvSwitchDriver
from ovm.vmcreation.vmnetwork import VMNetwork
from ovm.vmcreation.vmstorage import VMStorage

########################################################################


#
# Storage pools definition
#

STORAGES = {}

STORAGES['ssd'] = VMStorage(
    VolumeDriver,
    pool_name='pool-vm-ssd'
)

STORAGES['nfs'] = VMStorage(
    VolumeDriver,
    pool_name='pool-vm-nfs'
)


#
# Networks definition
#
NETWORKS = {}

NETWORKS['local'] = VMNetwork(
    OpenvSwitchDriver,
    net_name='net-ovs',
    net_portgroup='local',
    pool_ip={
        'ip_start': '192.168.1.30',
        'ip_end': '192.168.1.63',
        'netmask': 24,
        'gateway': '192.168.1.1',
        'nameservers': ['192.168.1.1'],
        'autoip_path': '/etc/autoip/local.dat'
    }
)

NETWORKS['prod'] = VMNetwork(
    OpenvSwitchDriver,
    net_name='net-ovs',
    net_portgroup='prod',
    pool_ip={
        'ip_start': '10.42.1.10',
        'ip_end': '10.42.1.254',
        'netmask': 24,
        'gateway': '10.42.1.1',
        'nameservers': ['10.42.1.1'],
        'autoip_path': '/etc/autoip/prod.dat'
    }
)