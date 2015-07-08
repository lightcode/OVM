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


import os
import stat
import sys
import tempfile
from subprocess import PIPE, Popen, STDOUT

from ovm.configuration import Configuration
from ovm.exceptions import OVMError
from ovm.inventory import Inventory
from ovm.resources.resources import Resources
from ovm.templates.domain_definition import DomainDefinition
from ovm.templates.template import Template
from ovm.utils.logger import logger


def _exec_script(path, cmd_params=None, env_params=None):
    if not path.startswith('/'):
        path = os.path.join(Configuration.ETC, 'scripts', path)

    if not os.path.exists(path):
        logger.warning('Script ignored "%s": not found', path)
        return

    os.chmod(path, stat.S_IXUSR)

    cmd = [path]
    if cmd_params:
        cmd += cmd_params

    env = os.environ.copy()
    if env_params:
        env.update(env_params)

    scriptname = os.path.basename(path)
    process = Popen(cmd, env=env, stdout=PIPE, stderr=STDOUT)
    for line in process.stdout:
        logger.debug('[%s] %s', scriptname, line.decode('utf-8').strip())


def _long_netmask(cidr):
    mask = 0xFFFFFFFF << (32 - cidr)
    return '.'.join([str(mask >> (8 * i) & 0xFF) for i in range(3, -1, -1)])


class VMCreation:

    STEPS = (
        'check_domain_name',
        'process_network_args',
        'process_storage_args',
        'build_domain_definition',
        'create_main_disk',
        'resize_main_filesystem',
        'running_post_install_scripts',
        'add_domain_in_inventory',
        'reserve_ip',
        'print_domain'
    )

    def __init__(self, args):
        self._args = args
        self._network = None
        self._storage = None
        self._domdef = None
        self._diskpath = None
        self._template = None
        self._params = None
        self._domain = None

    def start(self):
        for num, step in enumerate(self.STEPS, 1):
            logger.debug('Step n°%d: %s', num, step)
            try:
                getattr(self, step)(self._args)
            except OVMError as e:
                logger.error('Cannot create VM "%s": %s', self._args.name,
                             e.message)
                sys.exit(1)

    def check_domain_name(self, args):
        domains = [domain.get_name() for domain in Inventory.get_domains()]
        if args.name in domains:
            raise OVMError('this name is already taken by another VM.')

    def process_network_args(self, args):
        network = Resources.get_network(args.network)

        if args.ip == 'auto':
            network.set_ip_auto()
            network.set_ip_auto()
        elif args.ip == 'dhcp':
            network.set_ip_dhcp()
        elif args.ip == 'default':
            network.set_ip_default()
        else:
            network.set_ip_manual(args.ip)
        self._network = network

    def process_storage_args(self, args):
        self._storage = Resources.get_storage_pool(args.storage)

    def build_domain_definition(self, args):
        template = Template.get_template(args.template)
        logger.info('Template "%s" loaded.', template.name)

        self._network.import_template_spec(template)

        domdef = DomainDefinition(template, args.name)
        domdef.set_network(self._network)
        domdef.set_storage(self._storage)

        if args.vcpu:
            domdef.vcpu = args.vcpu

        if args.memory:
            domdef.memory = args.memory

        self._template = template
        self._domdef = domdef

    def create_main_disk(self, args):
        logger.info("Creating VM's disk...")
        self._diskpath = self._domdef.create_main_disk()
        if args.size:
            self._domdef.resize_main_disk(args.size)

    def resize_main_filesystem(self, args):
        options = self._template.abilities['resizeDisk']
        if not options:
            logger.debug('The template has no attribut "resizeDisk": '
                         'filesystem resize ignored')
            return

        logger.info('Resizing filesystem...')
        params = []
        for param in options['params']:
            params.append(param.format(vol_path=self._diskpath))
        _exec_script(options['script'], params)

    def running_post_install_scripts(self, args):
        network = self._network
        env = {}
        if network.is_dhcp():
            env['IP'] = 'dhcp'
        else:
            env['IP'] = str(network.ipv4_pool['ip'])
            env['NETMASK'] = _long_netmask(network.ipv4_pool['netmask'])
            env['GATEWAY'] = str(network.ipv4_pool['gateway'])
            env['NAMESERVERS'] = ' '.join(network.ipv4_pool['nameservers'])
        env['HOSTNAME'] = self._domdef.name

        self._params = env
        post_install = self._template.post_install

        if not post_install:
            return

        _, filename = tempfile.mkstemp()
        with open(filename, 'wb+') as configuration:
            for name, value in env.items():
                configuration.write(
                    bytes('{}={}\n'.format(name, value), 'utf-8'))

        logger.info('Running post-install scripts...')
        for hook in post_install:
            path = hook['path']
            params = hook['params']
            for i, param in enumerate(params):
                params[i] = param.format(
                    diskpath=self._diskpath,
                    configuration=filename)

            logger.debug('post-install: exec %s', path)
            _exec_script(path, params, env)

        os.remove(filename)

    def add_domain_in_inventory(self, args):
        Inventory.add_domain(self._domdef)
        domain = Inventory.get_domain(self._domdef.name)
        domain.set_main_ipv4(self._params['IP'])
        domain.metadata.update(self._template.metadata)
        self._domain = domain

    def reserve_ip(self, args):
        self._network.lock_ip()

    def print_domain(self, args):
        from ovm.vmcli.management import print_vm_info
        print('\n')
        print_vm_info(self._domain)
