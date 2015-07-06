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


from ipaddr import IPAddress


def _iter_range(ipstart, ipend):
    ipstart = IPAddress(ipstart)
    ipend = IPAddress(ipend)
    currentip = ipstart
    while currentip != ipend:
        yield currentip
        currentip += 1


class Network(object):
    def __init__(self, name, driver, ipv4_allocation=None, ipv4_pool=None,
                 options=None, **params):

        self.name = name
        self._method = None
        self._driver = driver()

        self._params = params

        options_default = {
            'allow_dhcp': False,
            'allow_auto': True
        }
        self.options = options_default
        if options:
            self.options.update(options)

        self.ipv4_allocation = ipv4_allocation
        self.ipv4_pool = ipv4_pool

        # Set driver params
        self._driver.set_params(**params)

    def _lock_ip(self):
        autoip_path = self.ipv4_pool['autoip_path']
        with open(autoip_path, 'a+') as file_:
            file_.write(self.ipv4_pool['ip'] + '\n')

    def lock_ip(self):
        if self._method in ('auto', 'manual'):
            self._lock_ip()

    def is_dhcp(self):
        return self._method == 'dhcp'

    def _get_used_ips(self):
        autoip_path = self.ipv4_pool['autoip_path']
        used_ips = []
        try:
            with open(autoip_path, 'r+') as autoip_file:
                for line in autoip_file:
                    used_ips.append(line.strip())
        except IOError:
            pass
        return used_ips

    def set_ip_auto(self):
        self._method = 'auto'
        ipchoose = None
        used_ips = self._get_used_ips()

        ipstart = self.ipv4_pool['ip_start']
        ipend = self.ipv4_pool['ip_end']

        for ip in _iter_range(ipstart, ipend):
            if str(ip) not in used_ips:
                ipchoose = str(ip)
                break

        if not ipchoose:
            raise Exception('No IPs available in your IP pool')

        self.ipv4_pool['ip'] = ipchoose

    def set_ip_default(self):
        if self.ipv4_allocation == 'static':
            self.set_ip_auto()
        else:
            self.set_ip_dhcp()

    def set_ip_dhcp(self):
        self._method = 'dhcp'

    def set_ip_manual(self, ip):
        self._method = 'manual'
        try:
            ip = IPAddress(ip)
        except ValueError:
            raise Exception('"%s" is not a valid IP address.' % ip)

        # Check if the IP is in the ipv4_pool
        ipstart = self.ipv4_pool['ip_start']
        ipend = self.ipv4_pool['ip_end']
        if ip not in _iter_range(ipstart, ipend):
            raise Exception('"%s" does not match with the pool.' % ip)

        # Check if the IP has already attributed
        used_ips = self._get_used_ips()
        if str(ip) in used_ips:
            raise Exception('This IP address has been provided.')

        self.ipv4_pool['ip'] = str(ip)

    def import_template_spec(self, template):
        model = template.main_interface['model']
        self._driver.set_params(driver_type=model)

    def get_xml(self):
        return self._driver.get_xml()
