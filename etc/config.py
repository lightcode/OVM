#!/usr/bin/python

# File        : config.py
# Author      : Matthieu
# Description : Config file for VM command


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
    pool_name='pool-vm-ssd')
STORAGES['nfs'] = VMStorage(
    VolumeDriver,
    pool_name='pool-vm-nfs')


#
# Networks definition
#
NETWORKS = {}

NETWORKS['local'] = VMNetwork(
    OpenvSwitchDriver,
    bridge_name='net-ovs',
    net_portgroup='local',
    pool_ip={
        'ip_start': '192.168.1.30',
        'ip_end': '192.168.1.63',
        'netmask': 24,
        'gateway': '192.168.1.1',
        'nameservers': ['192.168.1.1'],
        'autoip_path': '/var/kvm/scripts/vm/.app/local.net'
    }
)

NETWORKS['prod'] = VMNetwork(
    OpenvSwitchDriver,
    bridge_name='net-ovs',
    net_portgroup='prod',
    pool_ip={
        'ip_start': '10.42.1.10',
        'ip_end': '10.42.1.254',
        'netmask': 24,
        'gateway': '10.42.1.1',
        'nameservers': ['10.42.1.1'],
        'autoip_path': '/var/kvm/scripts/vm/.app/prod.net'
    }
)

NETWORKS['labs'] = VMNetwork(
    OpenvSwitchDriver,
    bridge_name='net-ovs',
    net_portgroup='labs',
    pool_ip={
        'ip_start': '10.42.2.10',
        'ip_end': '10.42.2.254',
        'netmask': 24,
        'gateway': '10.42.2.1',
        'nameservers': ['10.42.2.1'],
        'autoip_path': '/var/kvm/scripts/vm/.app/labs.net'
    }
)


# TEMPLATES_DIR = '/var/kvm/scripts/vm/templates'
# NETWORKS['zeroconf'] = VMNetwork(
#     TEMPLATES_DIR + '/net-bridge.xml',
#     tpl_params={
#         'network': 'net-zeroconf'
#     },
#     pool_ip={}
# )
