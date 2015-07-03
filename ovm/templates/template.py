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


import yaml


class Template(object):

    DEFAULT_VCPU = 1
    DEFAULT_MEMORY = 256
    DEFAULT_ABILITIES = {'resizeDisk': False}

    def __init__(self, config):
        self.uid = config.get('uid')
        self.name = config.get('name')
        self.vcpu = int(config.get('vcpu', Template.DEFAULT_VCPU))
        self.memory = int(config.get('memory', Template.DEFAULT_MEMORY))
        self.metadata = dict(config.get('metadata', {}))
        self.main_disk = dict(config.get('main_disk', {}))
        self.main_interface = dict(config.get('main_interface', {}))
        self.post_install = list(config.get('post_install', []))

        abilities = Template.DEFAULT_ABILITIES.copy()
        abilities.update(config.get('abilities', {}))
        self.abilities = abilities

    def get_os_type(self):
        return self.metadata.get('os_type')

    def get_os_name(self):
        return self.metadata.get('os_name')

    def get_os_version(self):
        return self.metadata.get('os_version')

    @classmethod
    def load_file(cls, ofile):
        config = yaml.load(ofile.read())
        return cls(config)
