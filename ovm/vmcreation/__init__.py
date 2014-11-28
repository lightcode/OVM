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


import concurrent.futures
import os
import stat
from pyvirt.libvirtconn import LibvirtConn
from ovm.app import App
from ovm.resources import Resources
from ovm.utils.printer import print_table, default
from ovm.vmcreation.vmdefinition import VMDefinition
from ovm.vmcreation.vmnetwork import VMNetwork
from ovm.vmcreation.vmstorage import VMStorage
from ovm.vmmanagement import print_vm_info
from subprocess import PIPE, Popen


STORAGES = Resources.get_storages()
NETWORKS = Resources.get_networks()
LEVEL_ERROR, LEVEL_INFO = 0, 1


def _resize_fs(template, vol_path, verbose=False):
    '''Resize VM's filesystem if it defined in template.
    '''
    tpl = template._config
    if 'abilities' in tpl and 'resizeDisk' in tpl['abilities']:
        print('Resizing filesystem...')
        options = tpl['abilities']['resizeDisk']
        params = []
        for param in options['params']:
            params.append(param.format(vol_path=vol_path))
        _exec_script(options['script'], params, verbose=verbose)
    return vol_path


def _thread_logger(fd, level, print_log):
    for line in fd:
        line = line.decode('utf8').rstrip()
        if level == LEVEL_ERROR:
            if print_log:
                App.notice(line)
        elif level == LEVEL_INFO:
            if print_log:
                App.info(line)


def _exec_script(path, cmd_params=None, env_params=None, verbose=False):
    if not path.startswith('/'):
        path = os.path.join(App.ETC, 'scripts', path)

    if not os.path.exists(path):
        print('Script ignored "{0}": not found'.format(path))
        return

    os.chmod(path, stat.S_IXUSR)

    cmd = [path]
    if cmd_params:
        cmd += cmd_params

    env = os.environ.copy()
    if env_params:
        env.update(env_params)

    process = Popen(cmd, env=env, stdout=PIPE, stderr=PIPE)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        threads = []
        threads.append(executor.submit(
            _thread_logger, process.stdout, LEVEL_INFO, verbose
        ))
        threads.append(executor.submit(
            _thread_logger, process.stderr, LEVEL_ERROR, verbose
        ))
        for future in concurrent.futures.as_completed(threads):
            if future.exception() is not None:
                print(future.exception())


def _post_install(template, diskpath, env_params, verbose=False):
    tpl = template._config
    if 'post-install' not in tpl:
        return
    print('Running post-install scripts...')
    for hook in tpl['post-install']:
        path = hook['path']
        params = hook['params']
        for i, param in enumerate(params):
            params[i] = param.format(diskpath=diskpath)
        _exec_script(path, params, env_params, verbose)


def _process_args_network(args):
    if args.network not in NETWORKS:
        App.fatal('Network "{0}" doesn\'t exists.'.format(args.network))

    network = NETWORKS[args.network]

    if args.ip == 'auto':
        network.set_ip_auto()
        try:
            network.set_ip_auto()
        except Exception as e:
            App.fatal(e)
    elif args.ip == 'dhcp':
        try:
            network.set_ip_dhcp()
        except Exception as e:
            App.fatal(e)
    elif args.ip == 'default':
        try:
            network.set_ip_default()
        except Exception as e:
            App.fatal(e)
    else:
        try:
            network.set_ip_manual(args.ip)
        except Exception as e:
            App.fatal(e)
    return network


def _long_netmask(cidr):
    mask = 0xFFFFFFFF << (32 - cidr)
    return '.'.join([str(mask >> (8 * i) & 0xFF) for i in range(3, -1, -1)])


def _process_args_storage(args):
    if args.storage not in STORAGES:
        App.fatal('Storage "{0}" does\'t exists.'.format(args.storage))

    storage = STORAGES[args.storage]

    if args.size:
        storage.set_size(args.size)

    return storage


def vm_create(args):
    domains = [domain.get_name() for domain in LibvirtConn.get_domains()]
    if args.name in domains:
        App.fatal('This name is already taken by another VM.')

    verbose = False
    if args.verbose:
        verbose = True

    network = _process_args_network(args)

    params = {}
    if network.is_dhcp():
        params['IP'] = 'dhcp'
    else:
        params['IP'] = str(network.ipv4_pool['ip'])
        params['NETMASK'] = _long_netmask(network.ipv4_pool['netmask'])
        params['GATEWAY'] = str(network.ipv4_pool['gateway'])
        params['NAMESERVERS'] = ' '.join(network.ipv4_pool['nameservers'])

    storage = _process_args_storage(args)

    # 1. Find the template
    App.load_templates()
    template = App.get_template(args.template)
    print('You choose the template {0}.'.format(template.get_name()))

    network.import_template_spec(template)

    vmd = VMDefinition(template, args.name)
    vmd.set_network(network)
    vmd.set_storage(storage)

    print("Creating VM's disk...")
    storage.import_template(template)
    storage.set_vmd(vmd)
    diskpath = storage.create_disk(template)

    if args.vcpu:
        vmd.set_vcpu(args.vcpu)

    if args.memory:
        vmd.set_memory(args.memory)

    # 2. Running post-install scripts
    params['HOSTNAME'] = vmd.name()
    _resize_fs(template, diskpath, verbose=verbose)
    _post_install(template, diskpath, params, verbose=verbose)

    # 3. Add the VM in libvirt
    xml = vmd.get_xml()
    LibvirtConn.define_domain(xml)

    domain = LibvirtConn.get_domain(vmd.name())
    domain.set_main_ipv4(params['IP'])
    domain.set_os_type(template.get_os_type())
    domain.set_os_name(template.get_os_name())
    domain.set_os_version(template.get_os_version())

    # 4. Lock network resources
    network.lock_ip()

    # 5. Print the VM specs
    print('\n')
    print_vm_info(domain)


def vm_templates(args):
    App.load_templates()
    templates = App.get_templates()

    if args.short:
        print('\n'.join([tpl.get_id() for tpl in templates]))
        return

    headers = ('ID', 'Name', 'OS type', 'OS name', 'OS version')
    rows = []
    for tpl in templates:
        rows.append((
            tpl.get_id(),
            tpl.get_name(),
            default(tpl.get_os_type(), '-'),
            default(tpl.get_os_name(), '-'),
            default(tpl.get_os_version(), '-')
        ))
    print_table(headers, rows)


def vm_storages(args):
    if args.short:
        print('\n'.join([k for k in STORAGES]))
        return

    headers = ('ID', 'Pool name')
    rows = []
    for name, storage in STORAGES.items():
        rows.append((name, storage.pool_name()))
    print_table(headers, rows)


def vm_networks(args):
    if args.short:
        print('\n'.join([k for k in NETWORKS]))
        return

    headers = ('ID',)
    rows = []
    for name, network in NETWORKS.items():
        rows.append((name,))
    print_table(headers, rows)