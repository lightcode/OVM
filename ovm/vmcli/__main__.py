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

from ovm.configuration import Configuration
from ovm.inventory import Inventory
from ovm.utils.logger import logger
from ovm.vmcli.management import *  # noqa


def add_subparsers(parser):
    subparsers = parser.add_subparsers()

    # console
    subcommand = subparsers.add_parser(
        'console',
        help='enter in the VM console')
    subcommand.add_argument('name', help='name of the VM')
    subcommand.set_defaults(func=vm_console)

    # create
    subcommand = subparsers.add_parser('create', help='create a new VM')
    subcommand.add_argument('name', help='set the name of the VM')
    subcommand.add_argument('--template', required=True)
    subcommand.add_argument('--network', required=True)
    subcommand.add_argument('--storage', required=True)
    subcommand.add_argument('--ip', nargs='?', default='default')
    subcommand.add_argument('--size', nargs='?')
    subcommand.add_argument('--vcpu', nargs='?')
    subcommand.add_argument('--memory', nargs='?')
    subcommand.set_defaults(func=vm_create)

    # templates
    subcommand = subparsers.add_parser(
        'templates',
        help='list templates')
    subcommand.add_argument(
        '--short',
        action='store_true',
        help='print only the list of templates names')
    subcommand.set_defaults(func=vm_templates)

    # storage
    subcommand = subparsers.add_parser('storage', help='list storage')
    subcommand.add_argument(
        '--short',
        action='store_true',
        help='print only the list of storage names')
    subcommand.set_defaults(func=vm_storage)

    # networks
    subcommand = subparsers.add_parser('networks', help='list networks')
    subcommand.add_argument(
        '--short',
        action='store_true',
        help='print only the list of networks names')
    subcommand.set_defaults(func=vm_networks)

    # list
    subcommand = subparsers.add_parser(
        'list',
        aliases=['ls'],
        help='list VMs')
    subcommand.add_argument(
        '--short',
        action='store_true',
        help='print only the list of VM names')
    subcommand.add_argument(
        '--active',
        action='store_true',
        help='print only the list of active VM')
    subcommand.add_argument(
        '--inactive',
        action='store_true',
        help='print only the list of inactive VM')
    subcommand.set_defaults(func=vm_list)

    # set
    subcommand = subparsers.add_parser('set', help='set a metadata on a vm')
    subcommand.add_argument('name', help='name of the VM')
    subcommand.add_argument(
        'metadata',
        nargs='+',
        help='enter metadata as <key>=<value>')
    subcommand.set_defaults(func=vm_set)

    # unset
    subcommand = subparsers.add_parser(
        'unset',
        help='unset a metadata on a vm')
    subcommand.add_argument('name', help='name of the VM')
    subcommand.add_argument('key', nargs='+')
    subcommand.set_defaults(func=vm_unset)

    # autostart
    subcommand = subparsers.add_parser(
        'autostart',
        help='choose if the VM starts automatically at boot')
    subcommand.add_argument('name', help='name of the VM')
    subcommand.add_argument('value', choices=['on', 'off'])
    subcommand.set_defaults(func=vm_autostart)

    # start
    subcommand = subparsers.add_parser(
        'start',
        help='start one or many VMs')
    subcommand.add_argument('name', nargs='+', help='name of VMs')
    subcommand.set_defaults(func=vm_start)

    # info
    subcommand = subparsers.add_parser(
        'info',
        help='show information about a VM')
    subcommand.add_argument('name', help='name of the VM')
    subcommand.set_defaults(func=vm_info)

    # reboot
    subcommand = subparsers.add_parser('reboot', help='reboot a VM')
    subcommand.add_argument('name', help='name of the VM')
    subcommand.set_defaults(func=vm_reboot)

    # save
    subcommand = subparsers.add_parser('save', help='save a VM')
    subcommand.add_argument('name', nargs='+', help='name of VMs')
    subcommand.set_defaults(func=vm_save)

    # restore
    subcommand = subparsers.add_parser('restore', help='restore a VM')
    subcommand.add_argument('name', nargs='+', help='name of VMs')
    subcommand.set_defaults(func=vm_restore)

    # stop
    subcommand = subparsers.add_parser('stop', help='stop one or many VMs')
    subcommand.add_argument('name', nargs='+', help='name of VMs')
    subcommand.add_argument(
        '-f', '--force',
        action='store_true',
        help='force the VM shutdown')
    subcommand.set_defaults(func=vm_stop)

    # remove
    subcommand = subparsers.add_parser(
        'remove', aliases=['rm'],
        help='remove one or many VMs')
    subcommand.add_argument('name', help='name of VMs', nargs='+')
    subcommand.add_argument(
        '-f', '--force', '--yes', '-y',
        action='store_true',
        dest='force',
        help='Remove VM without asking confirmation.')
    subcommand.set_defaults(func=vm_remove)

    # ssh
    subcommand = subparsers.add_parser('ssh', help='ssh a VM')
    subcommand.add_argument('name', help='name of the VM')
    subcommand.set_defaults(func=vm_ssh)

    # ping
    subcommand = subparsers.add_parser('ping', help='ping a VM')
    subcommand.add_argument('name', help='name of the VM')
    subcommand.set_defaults(func=vm_ping)

    # top
    subcommand = subparsers.add_parser(
        'top',
        help='show all VMs and their states')
    subcommand.set_defaults(func=vm_top)


def main():
    # Ignore text error from libvirt
    libvirt.registerErrorHandler(lambda: 1, None)

    parser = argparse.ArgumentParser(
        description='Provide functions to create and manage VMs on KVM.',
        prog='vm')
    parser.add_argument('--version', action='version',
                        version=Configuration.VERSION)
    parser.add_argument('-v', '--verbose', action='store_true')

    add_subparsers(parser)

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    Resources(Configuration.RESOURCE_CONFIG)
    Inventory.open()

    if hasattr(args, 'func'):
        getattr(args, 'func')(args)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
