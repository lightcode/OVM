#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
########################################################################
# Copyright 2015 Matthieu Gaignière                  http://lightcode.fr
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


import libvirt
import concurrent.futures
from subprocess import Popen

from ovm.app import App
from ovm.exceptions import DomainException
from ovm.exceptions import OVMError
from ovm.inventory import Inventory
from ovm.resources import Resources
from ovm.templates.template import Template
from ovm.utils.logger import logger
from ovm.utils.printer import ColoredString, bcolors
from ovm.utils.printer import print_title, si_unit, default, print_table
from ovm.vmcli.creation import VMCreation
from ovm.vmcli.libvirt_console import Console
from ovm.vmcli.vmtop import VMTop


ENABLE_CONCURRENT = False


###################################
# MISCELLANEOUS FUNCTIONS
###################################

def _get_domain(name):
    try:
        domain = Inventory.get_domain(name)
    except libvirt.libvirtError:
        raise OVMError('Cannot get the VM "%s".' % name)
    else:
        return domain


def bulk_command(func):
    def wrapper(*args, **kwargs):
        cli_args = args[0]
        vmnames = cli_args.name
        if isinstance(vmnames, str):
            vmnames = [vmnames]

        if not ENABLE_CONCURRENT:
            for name in vmnames:
                try:
                    func(name, cli_args)
                except OVMError as e:
                    logger.error(e.message)
                except:
                    logger.exception('Unhandled exception:')
            return

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            tasks = {}
            for name in vmnames:
                tasks[executor.submit(func, name, cli_args)] = name

            for future in concurrent.futures.as_completed(tasks):
                if future.exception() is not None:
                    logger.error('Unhandled error for %s: %s',
                                 name, future.exception())
    return wrapper


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

    print_title('Network')
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

    print_title('Storage')
    headers = ['Target', 'Path', 'Pool', 'Real size']
    align = ('l', 'l', 'l', 'l')
    rows = []
    for vol in domain.get_disks():
        rows.append((
            vol.guest_dev,
            vol.path,
            vol.pool.name,
            '%sB' % si_unit(vol.size, True)
        ))
    print_table(headers, rows, align)
    print()
    print()

    print_title('Metadata')
    for name, value in domain.metadata:
        print('{}={}'.format(name, value))
    print()


def vm_autostart(args):
    domain = _get_domain(args.name)
    if args.value == 'on':
        domain.set_autostart(True)
    else:
        domain.set_autostart(False)


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

    for domain in Inventory.get_domains():
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
    with Popen(cmd) as process:
        try:
            process.communicate()
        except KeyboardInterrupt:
            pass


def vm_reboot(args):
    virdomain = _get_domain(args.name).vir_domain
    if not virdomain.isActive():
        App.fatal('VM must be active.')
    virdomain.reset()


@bulk_command
def vm_remove(name, args):
    ans = ''
    while not args.force and ans not in ('y', 'n'):
        ans = input('Delete VM "%s" and all disks? [y/n] ' % name)
        ans = ans.strip().lower()

    if ans == 'n':
        logger.info('Deletion of "%s" aborted by user.', name)
        return

    domain = _get_domain(name)
    try:
        res = domain.remove()
    except DomainException as e:
        logger.error('Error: the VM cannot be removed: %s', e.message)
        return
    else:
        if res == 0:
            logger.info('The domain has been removed.')
        else:
            logger.error('Libvirt return error code %d.', res)


def vm_set(args):
    domain = _get_domain(args.name)
    for metadata in args.metadata:
        try:
            key, value = metadata.split('=', 1)
        except ValueError:
            logger.warning('Ignore "%s": not in a good format.', metadata)
        else:
            domain.metadata[key] = value
    domain.metadata.save()


def vm_unset(args):
    domain = _get_domain(args.name)
    for key in args.key:
        try:
            del domain.metadata[str(key)]
        except KeyError:
            logger.warning('Cannot delete "%s": key does not exist.', key)
    domain.metadata.save()


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

    with Popen(cmd) as process:
        try:
            process.communicate()
        except KeyboardInterrupt:
            pass


@bulk_command
def vm_start(name, args):
    domain = _get_domain(name)
    if domain.is_active():
        logger.warning('VM "%s" is already active.', name)
    else:
        domain.start()
        info_string = 'VM "{0}" started with '.format(name)

        ipv4 = domain.get_main_ipv4()
        have_ipv4 = not ipv4 or ipv4 == 'dhcp'
        if have_ipv4:
            info_string += 'no static IP'
        else:
            info_string += 'IP {0}'.format(ipv4)

        info_string += ' and '

        domain = _get_domain(name)
        vnc = domain.get_vnc_info()
        if vnc and 'screen' in vnc and vnc['screen']:
            info_string += 'the VNC screen number {0}'.format(vnc['screen'])
        else:
            info_string += 'no VNC screen'

        logger.info('%s.', info_string)


@bulk_command
def vm_save(name, args):
    try:
        domain = _get_domain(name)
        domain.save()
    except OVMError as e:
        logger.error('VM "%s" cannot be saved: %s', name, e)
    else:
        logger.info('VM "%s" is saved.')


@bulk_command
def vm_restore(name, args):
    try:
        domain = _get_domain(name)
        domain.save()
    except OVMError as e:
        logger.error('VM "%s" cannot be restored: %s', name, e)
    else:
        logger.info('VM "%s" is restored.')


@bulk_command
def vm_stop(name, args):
    virdomain = _get_domain(name).vir_domain
    if not virdomain.isActive():
        logger.warning('Cannot stop "%s": it already inactive.', name)
    else:
        if args.force:
            virdomain.destroy()
        else:
            virdomain.shutdown()
        logger.info('VM "%s" stopped.', name)


def vm_top(_):
    VMTop()


def vm_storage(args):
    if args.short:
        print('\n'.join([p.name for p in Resources.get_storage_pools()]))
        return

    headers = ('Pool name',)
    rows = []
    for storage in Resources.get_storage_pools():
        rows.append((storage.name,))
    print_table(headers, rows)


def vm_networks(args):
    if args.short:
        print('\n'.join([n.name for n in Resources.get_networks()]))
        return

    headers = ('Network name',)
    rows = []
    for network in Resources.get_networks():
        rows.append((network.name,))
    print_table(headers, rows)


def vm_create(args):
    vmc = VMCreation(args)
    vmc.start()


def vm_templates(args):
    templates = list(Template.get_templates())

    if args.short:
        print('\n'.join([tpl.uid for tpl in templates]))
        return

    headers = ('ID', 'Name', 'OS type', 'OS name', 'OS version')
    rows = []
    for tpl in templates:
        rows.append((
            tpl.uid,
            tpl.name,
            default(tpl.get_os_type(), '-'),
            default(tpl.get_os_name(), '-'),
            default(tpl.get_os_version(), '-')
        ))
    print_table(headers, rows)
