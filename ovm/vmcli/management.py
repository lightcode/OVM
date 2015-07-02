#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
########################################################################
# Copyright 2014 Matthieu Gaignière                  http://lightcode.fr
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


import sys
from subprocess import Popen

import libvirt
from ovm.libvirt_driver.libvirtconn import LibvirtConn
from ovm.utils.printer import print_title, si_unit, default, print_table
from ovm.utils.printer import ColoredString, bcolors
from ovm.app import App
from ovm.vmcli.libvirt_console import Console
from ovm.vmcli.vmtop import VMTop


###################################
# MISCELLANEOUS FUNCTIONS
###################################

def _get_domain(name):
    try:
        domain = LibvirtConn.get_domain(name)
    except libvirt.libvirtError:
        App.fatal('Cannot get the VM "%s".' % name)
    else:
        return domain


def _apply_on_vms(names, function, success_message, error_message):
    error_count = 0
    for name in names:
        try:
            function(_get_domain(name))
        except Exception as e:
            App.notice('Error on {0}: {1}'.format(name, e))
            error_count += 1
        else:
            App.success(success_message.format(name))

    if error_count > 0:
        App.fatal(error_message.format(error_count))


###################################
# VM MANAGEMENT FUNCTIONS
###################################

def print_vm_info(domain):
    print_title('Information about VM {0}'.format(domain.get_name()))
    print('OS name        : {0}'.format(domain.get_os_string()))
    print('State          : {0}'.format(domain.get_state_text()))
    print('vCPU number    : {0}'.format(domain.get_vcpu_count()))
    print('Current memory : {0}B'.format(
        si_unit(domain.get_current_memory(), True)))
    print('Maximum memory : {0}B'.format(si_unit(domain.get_memory(), True)))
    print('IP address     : {0}'.format(domain.get_main_ipv4()))
    print('Starting       : {0}'.format(
        'Auto' if domain.get_autostart() else 'Manual'))
    print('VNC screen     : {0}'.format(domain.get_vnc_info()['screen']))
    print()
    print()

    print_title('Interfaces')
    headers = ['MAC address', 'Network', 'Port group']
    rows = []
    for iface in domain.get_interfaces():
        rows.append((
            iface.get_mac(),
            iface.get_network_name(),
            iface.get_portgroup()
        ))
    print_table(headers, rows)
    print()
    print()

    print_title('Volumes')
    headers = ['Name', 'Pool', 'Capacity', 'Allocation']
    align = ('l', 'l', 'r', 'r')
    rows = []
    for vol in domain.get_volumes():
        rows.append((
            vol.get_name(),
            vol.get_pool_name(),
            '%sB' % si_unit(vol.get_capacity(), True),
            '%sB' % si_unit(vol.get_allocation(), True)
        ))
    print_table(headers, rows, align)
    print()
    print()

    print_title('Metadata')
    for name, value in domain.metadata:
        print('{}={}'.format(name, value))
    print()


def vm_info(args):
    domain = _get_domain(args.name)
    print_vm_info(domain)


def vm_list(args):
    headers = ('Name', 'vCPU', 'Cur. memory', 'Starting',
               'State', 'IP', 'OS name')
    align = ('l', 'r', 'r', 'l', 'l', 'l', 'l')
    rows = []

    if args.active and args.inactive:
        App.fatal('A VM cannot be active and inactive.')

    for domain in LibvirtConn.get_domains():
        virdomain = domain.vir_domain

        if (args.active and not virdomain.isActive()) \
                or (args.inactive and virdomain.isActive()):
            continue

        state = domain.get_state_text()
        if state == 'Running':
            state = ColoredString('Running', bcolors.OKGREEN)
        elif state == 'Stopped':
            state = ColoredString('Stopped', bcolors.FAIL)

        main_ip = domain.get_main_ipv4()
        rows.append((
            domain.get_name(), domain.get_vcpu_count(),
            '%sB' % si_unit(domain.get_current_memory(), True),
            'Auto' if domain.get_autostart() else 'Manual',
            state,
            default(main_ip, '-'),
            default(domain.get_os_string(), '-')
        ))

    rows.sort(key=lambda e: e[0])

    if args.short:
        for line in rows:
            print(line[0])
    else:
        print_table(headers, rows, align)


def vm_ping(args):
    domain = _get_domain(args.name)
    virdomain = domain.vir_domain

    if not virdomain.isActive():
        App.fatal('Cannot ping an inactive VM.')

    ipv4 = domain.get_main_ipv4()
    if not ipv4 or ipv4 == 'dhcp':
        App.fatal('Cannot ping a VM with no IP.')

    cmd = ['ping', ipv4]
    process = Popen(cmd)
    try:
        process.communicate()
    except KeyboardInterrupt:
        pass


def vm_reboot(args):
    virdomain = _get_domain(args.name).vir_domain
    if not virdomain.isActive():
        App.fatal('VM must be active.')
    virdomain.reset()


def _remove_vm(name, force):
    res = None
    while not force and res not in ('y', 'n'):
        res = input('Delete VM "%s" and all disks? [y/N] ' % name)
        res = res.lower()

    if res == 'n':
        App.notice('Deletion of "{0}" aborted by user.'.format(name))
        return False

    domain = _get_domain(name)
    try:
        res = domain.remove()
    except Exception as e:
        App.notice('Error: the VM cannot be removed: %s' % e)
        return False
    else:
        if res == 0:
            print('The domain has been removed.')
            return True
        else:
            App.notice('Error %d: the VM cannot be removed.' % res)
            return False


def vm_remove(args):
    error_count = 0
    for name in args.name:
        if not _remove_vm(name, args.yes):
            error_count += 1

    if error_count > 0:
        App.fatal('{0} VMs cannot be deleted.'.format(error_count))


def vm_set(args):
    domain = _get_domain(args.name)
    domain.metadata[args.key] = args.value


def vm_console(args):
    domain = _get_domain(args.name)
    virdomain = domain.vir_domain

    if not virdomain.isActive():
        App.fatal('Cannot connect on an inactive VM.')

    Console.open_console(domain.get_name())


def vm_ssh(args):
    domain = _get_domain(args.name)
    virdomain = domain.vir_domain

    if not virdomain.isActive():
        App.fatal('Cannot connect on an inactive VM.')

    ipv4 = domain.get_main_ipv4()
    if not ipv4:
        App.fatal('Cannot connect on a VM with no IP.')

    cmd = ['ssh', '-q', '-o UserKnownHostsFile=/dev/null',
           '-o StrictHostKeyChecking=no', '-lroot', ipv4]
    process = Popen(cmd)
    try:
        process.communicate()
    except KeyboardInterrupt:
        pass


def vm_start(args):
    error_count = 0
    for name in args.name:
        domain = _get_domain(name)
        if domain.is_active():
            error_count += 1
            App.notice('VM "{0}" is already active.'.format(name))
        else:
            domain.start()
            App.success('VM "{0}" started with '.format(name), newline=False)

            ipv4 = domain.get_main_ipv4()
            have_ipv4 = not ipv4 or ipv4 == 'dhcp'
            if have_ipv4:
                sys.stdout.write('no static IP')
            else:
                sys.stdout.write('IP {0}'.format(ipv4))

            sys.stdout.write(' and ')

            domain = _get_domain(name)
            vnc = domain.get_vnc_info()
            if vnc and 'screen' in vnc and vnc['screen']:
                sys.stdout.write(
                    'the VNC screen number {0}'.format(vnc['screen']))
            else:
                sys.stdout.write('no VNC screen')

            sys.stdout.write('.\n')
            sys.stdout.flush()

    if error_count > 0:
        App.fatal('{0} VMs cannot be started.'.format(error_count))


def vm_save(args):
    _apply_on_vms(
        args.name,
        lambda domain: domain.save(),
        '{0} is saved.',
        '{0} VMs cannot be saved.'
    )


def vm_restore(args):
    _apply_on_vms(
        args.name,
        lambda domain: domain.restore(),
        '{0} is restored.',
        '{0} VMs cannot be restored.'
    )


def vm_stop(args):
    error_count = 0
    for name in args.name:
        virdomain = _get_domain(name).vir_domain
        if not virdomain.isActive():
            error_count += 1
            App.notice('VM "{0}" must be active.'.format(name))
        else:
            if args.force:
                virdomain.destroy()
            else:
                virdomain.shutdown()

    if error_count > 0:
        App.fatal('{0} VMs cannot be stopped.'.format(error_count))


def vm_top(args):
    VMTop()
