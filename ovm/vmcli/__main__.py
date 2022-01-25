#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import libvirt
import logging

from ovm.configuration import Configuration
from ovm.utils.logger import logger
from ovm.vmcli.management import *  # noqa


def add_subparsers(parser):
    subparsers = parser.add_subparsers()

    # console
    subcommand = subparsers.add_parser("console", help="enter in the VM console")
    subcommand.add_argument("name", help="name of the VM")
    subcommand.set_defaults(func=vm_console)

    # create
    subcommand = subparsers.add_parser("create", help="create a new VM")
    subcommand.add_argument("name", help="set the name of the VM")
    subcommand.add_argument("--template", required=True)
    subcommand.add_argument("--network", required=True)
    subcommand.add_argument("--storage", required=True)
    subcommand.add_argument("--ip", nargs="?")
    subcommand.add_argument("--size", nargs="?")
    subcommand.add_argument("--vcpu", nargs="?")
    subcommand.add_argument("--memory", nargs="?")
    subcommand.set_defaults(func=vm_create)

    # templates
    subcommand = subparsers.add_parser("templates", help="list templates")
    subcommand.add_argument(
        "--short", action="store_true", help="print only the list of templates names"
    )
    subcommand.set_defaults(func=vm_templates)

    # storage
    subcommand = subparsers.add_parser("storage", help="list storage")
    subcommand.add_argument(
        "--short", action="store_true", help="print only the list of storage names"
    )
    subcommand.set_defaults(func=vm_storage)

    # list
    subcommand = subparsers.add_parser("ls", help="list VMs")
    subcommand.add_argument(
        "--short", action="store_true", help="print only the list of VM names"
    )
    subcommand.add_argument(
        "--active", action="store_true", help="print only the list of active VM"
    )
    subcommand.add_argument(
        "--inactive", action="store_true", help="print only the list of inactive VM"
    )
    subcommand.set_defaults(func=vm_list)

    # set
    subcommand = subparsers.add_parser("set", help="set a metadata on a vm")
    subcommand.add_argument("name", help="name of the VM")
    subcommand.add_argument(
        "metadata", nargs="+", help="enter metadata as <key>=<value>"
    )
    subcommand.set_defaults(func=vm_set)

    # unset
    subcommand = subparsers.add_parser("unset", help="unset a metadata on a vm")
    subcommand.add_argument("name", help="name of the VM")
    subcommand.add_argument("key", nargs="+")
    subcommand.set_defaults(func=vm_unset)

    # autostart
    subcommand = subparsers.add_parser(
        "autostart", help="choose if the VM starts automatically at boot"
    )
    subcommand.add_argument("name", help="name of the VM")
    subcommand.add_argument("value", choices=["on", "off"])
    subcommand.set_defaults(func=vm_autostart)

    # start
    subcommand = subparsers.add_parser("start", help="start one or many VMs")
    subcommand.add_argument("name", nargs="+", help="name of VMs")
    subcommand.set_defaults(func=vm_start)

    # info
    subcommand = subparsers.add_parser("info", help="show information about a VM")
    subcommand.add_argument("name", help="name of the VM")
    subcommand.set_defaults(func=vm_info)

    # reboot
    subcommand = subparsers.add_parser("reboot", help="reboot a VM")
    subcommand.add_argument("name", help="name of the VM")
    subcommand.set_defaults(func=vm_reboot)

    # save
    subcommand = subparsers.add_parser("save", help="save a VM")
    subcommand.add_argument("name", nargs="+", help="name of VMs")
    subcommand.set_defaults(func=vm_save)

    # restore
    subcommand = subparsers.add_parser("restore", help="restore a VM")
    subcommand.add_argument("name", nargs="+", help="name of VMs")
    subcommand.set_defaults(func=vm_restore)

    # stop
    subcommand = subparsers.add_parser("stop", help="stop one or many VMs")
    subcommand.add_argument("name", nargs="+", help="name of VMs")
    subcommand.add_argument(
        "-f", "--force", action="store_true", help="force the VM shutdown"
    )
    subcommand.set_defaults(func=vm_stop)

    # remove
    subcommand = subparsers.add_parser("rm", help="remove one or many VMs")
    subcommand.add_argument("name", help="name of VMs", nargs="+")
    subcommand.add_argument(
        "-f",
        "--force",
        action="store_true",
        dest="force",
        help="Remove VM without asking confirmation.",
    )
    subcommand.set_defaults(func=vm_remove)

    # ssh
    subcommand = subparsers.add_parser("ssh", help="ssh a VM")
    subcommand.add_argument("name", help="name of the VM")
    subcommand.set_defaults(func=vm_ssh)

    # ping
    subcommand = subparsers.add_parser("ping", help="ping a VM")
    subcommand.add_argument("name", help="name of the VM")
    subcommand.set_defaults(func=vm_ping)

    # top
    subcommand = subparsers.add_parser("top", help="show all VMs and their states")
    subcommand.set_defaults(func=vm_top)

    # networks
    subcommand = subparsers.add_parser("network")
    add_network_subparsers(subcommand)


def add_network_subparsers(parser):
    subparsers = parser.add_subparsers()

    cmd = subparsers.add_parser("list")
    cmd.add_argument(
        "--short", action="store_true", help="print only the list of networks names"
    )
    cmd.set_defaults(func=network_list)

    cmd = subparsers.add_parser("ipv4-list", help="show IPv4 allocated to a network")
    cmd.add_argument("network")
    cmd.set_defaults(func=network_ipv4_list)

    cmd = subparsers.add_parser(
        "ipv4-del", help="delete an IPv4 associated with a network"
    )
    cmd.add_argument("network")
    cmd.add_argument("address", nargs="+")
    cmd.set_defaults(func=network_ipv4_delete)

    cmd = subparsers.add_parser(
        "ipv4-add", help="add a new association between a domain and an IP address"
    )
    cmd.add_argument("network")
    cmd.add_argument("domain")
    cmd.add_argument("address", nargs="?")
    cmd.set_defaults(func=network_ipv4_add)

    cmd = subparsers.add_parser("ipv4-flush", help="remove all ip address in a network")
    cmd.add_argument("network")
    cmd.set_defaults(func=network_ipv4_flush)


def main():
    # Ignore text error from libvirt
    libvirt.registerErrorHandler(lambda: 1, None)

    parser = argparse.ArgumentParser(
        description="Provide functions to create and manage VMs on KVM.", prog="vm"
    )
    parser.add_argument("--version", action="version", version=Configuration.VERSION)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument(
        "--fork", default=4, type=int, help="set how many tasks launch parallelly"
    )

    add_subparsers(parser)

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    Resources(Configuration.RESOURCE_CONFIG)

    if hasattr(args, "func"):
        getattr(args, "func")(args)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
