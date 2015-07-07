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


import argparse
import libvirt
import logging

from ovm.app import App
from ovm.inventory import Inventory
from ovm.utils.logger import logger
from ovm.vmcli.creation import *
from ovm.vmcli.management import *


# Don't show error message from libvirt_driver
def f(ctx, error):
    return 1


libvirt.registerErrorHandler(f, None)

App.init()
Inventory.open()


def parse_args():
    parser = argparse.ArgumentParser(
        description='Provide functions to create and manage VMs on KVM.',
        prog='vm')
    parser.add_argument('--version', action='version', version='OVM 0.2')
    parser.add_argument('-v', '--verbose', action='store_true')

    subparsers = parser.add_subparsers()

    # Enter in the VM console
    parser_console = subparsers.add_parser(
        'console', help='enter in the VM console')
    parser_console.add_argument('name', help='name of the VM')
    parser_console.set_defaults(func=vm_console)

    # Create a VM
    parser_create = subparsers.add_parser('create', help='create a new VM')
    parser_create.add_argument('name', help='set the name of the VM')
    parser_create.add_argument('--template', required=True)
    parser_create.add_argument('--network', required=True)
    parser_create.add_argument('--storage', required=True)
    parser_create.add_argument('--ip', nargs='?', default='default')
    parser_create.add_argument('--size', nargs='?')
    parser_create.add_argument('--vcpu', nargs='?')
    parser_create.add_argument('--memory', nargs='?')
    parser_create.set_defaults(func=vm_create)

    # List templates
    parser_templates = subparsers.add_parser(
        'templates', help='list templates')
    parser_templates.add_argument(
        '--short', action='store_true',
        help="print only the list of templates names")
    parser_templates.set_defaults(func=vm_templates)

    # List storage
    parser_storage = subparsers.add_parser('storage', help='list storage')
    parser_storage.add_argument(
        '--short', action='store_true',
        help='print only the list of storage names')
    parser_storage.set_defaults(func=vm_storage)

    # List networks
    parser_networks = subparsers.add_parser('networks', help='list networks')
    parser_networks.add_argument(
        '--short', action='store_true',
        help="print only the list of networks names")
    parser_networks.set_defaults(func=vm_networks)

    # List VMs
    parser_list = subparsers.add_parser(
        'list', aliases=['ls'], help='list VMs')
    parser_list.add_argument(
        '--short', action='store_true',
        help="print only the list of VM names")
    parser_list.add_argument(
        '--active', action='store_true',
        help="print only the list of active VM")
    parser_list.add_argument(
        '--inactive', action='store_true',
        help="print only the list of inactive VM")
    parser_list.set_defaults(func=vm_list)

    # Set metadata on a vm
    subcommand = subparsers.add_parser('set', help='set a metadata on a vm')
    subcommand.add_argument('name', help='name of the VM')
    subcommand.add_argument('metadata',
                            nargs='+',
                            help='enter metadata as <key>=<value>')
    subcommand.set_defaults(func=vm_set)

    # Unset metadata on a vm
    subcommand = subparsers.add_parser(
        'unset', help='unset a metadata on a vm')
    subcommand.add_argument('name', help='name of the VM')
    subcommand.add_argument('key', nargs='+')
    subcommand.set_defaults(func=vm_unset)

    # Autostart
    subcommand = subparsers.add_parser(
        'autostart', help='choose if the VM starts automatically at boot')
    subcommand.add_argument('name', help='name of the VM')
    subcommand.add_argument('value', choices=['on', 'off'])
    subcommand.set_defaults(func=vm_autostart)

    # Start a VM
    parser_start = subparsers.add_parser(
        'start', help='start one or many VMs')
    parser_start.add_argument('name', nargs='+', help='name of VMs')
    parser_start.set_defaults(func=vm_start)

    # Show information about a VM
    parser_info = subparsers.add_parser(
        'info', help='show information about a VM')
    parser_info.add_argument('name', help='name of the VM')
    parser_info.set_defaults(func=vm_info)

    # Reboot a VM
    parser_reboot = subparsers.add_parser('reboot', help='reboot a VM')
    parser_reboot.add_argument('name', help='name of the VM')
    parser_reboot.set_defaults(func=vm_reboot)

    # Save a VM
    parser_save = subparsers.add_parser('save', help='save a VM')
    parser_save.add_argument('name', nargs='+', help='name of VMs')
    parser_save.set_defaults(func=vm_save)

    # Restore a VM
    parser_restore = subparsers.add_parser('restore', help='restore a VM')
    parser_restore.add_argument('name', nargs='+', help='name of VMs')
    parser_restore.set_defaults(func=vm_restore)

    # Stop a VM
    parser_stop = subparsers.add_parser('stop', help='stop one or many VMs')
    parser_stop.add_argument('name', nargs='+', help='name of VMs')
    parser_stop.add_argument(
        '-f', '--force', action='store_true', help='force the VM shutdown')
    parser_stop.set_defaults(func=vm_stop)

    # Remove a VM
    parser_remove = subparsers.add_parser(
        'remove', aliases=['rm'], help='remove one or many VMs')
    parser_remove.add_argument('name', help='name of VMs', nargs='+')
    parser_remove.add_argument(
        '-f', '--force', '--yes', '-y', action='store_true',
        dest='force',
        help='Remove VM without asking confirmation.')
    parser_remove.set_defaults(func=vm_remove)

    # SSH
    parser_ssh = subparsers.add_parser('ssh', help='ssh a VM')
    parser_ssh.add_argument('name', help='name of the VM')
    parser_ssh.set_defaults(func=vm_ssh)

    # ping
    parser_ping = subparsers.add_parser('ping', help='ping a VM')
    parser_ping.add_argument('name', help='name of the VM')
    parser_ping.set_defaults(func=vm_ping)

    parser_top = subparsers.add_parser(
        'top', help='show all VMs and their states')
    parser_top.set_defaults(func=vm_top)

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    if hasattr(args, 'func'):
        getattr(args, 'func')(args)
    else:
        parser.print_help()
        sys.exit(0)


def main():
    parse_args()


if __name__ == "__main__":
    main()
