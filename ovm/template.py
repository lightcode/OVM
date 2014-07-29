#!/usr/bin/env python
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


import json
from ovm.utils.minify_json import json_minify


DEFAULT_ABILITIES = {
    'resizeDisk': False
}


class Template(object):

    def __init__(self, config):
        self._config = config

    def get_name(self):
        return self._config['name']

    def get_default_vcpu(self):
        vcpu = None
        if 'vcpu' in self._config:
            vcpu = self._config['vcpu']
        return vcpu

    def get_default_memory(self):
        memory = None
        if 'memory' in self._config:
            memory = self._config['memory']
        return memory

    def get_path(self):
        return self._config['main_disk']['path']

    def get_id(self):
        return self._config['id']
    
    @classmethod
    def load_json(cls, ofile):
        config = json.loads(json_minify(ofile.read()))
        abilities = DEFAULT_ABILITIES.copy()
        if 'abilities' in config:
            abilities.update(config['abilities'])
        return cls(config)
