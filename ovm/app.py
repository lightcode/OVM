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


import os
import sys
from glob import iglob
from ovm.resources import Resources
from ovm.singleton import Singleton
from ovm.template import Template
from ovm.utils.printer import bcolors, ColoredString


class App(Singleton):
    templates = []
    _templates_loaded = False
    ETC = '/etc/ovm'
    LOG_TYPE_SIZE = 7

    @classmethod
    def init(cls):
        Resources.init(os.path.join(cls.ETC, 'resources.yml'))

    @classmethod
    def load_templates(cls):
        if cls._templates_loaded:
            return

        for path in iglob(ETC_TEMPLATES):
            with open(path) as ofile:
                cls.templates.append(Template.load_file(ofile))

    @classmethod
    def get_templates(cls):
        return cls.templates

    @classmethod
    def get_template(cls, id_):
        for tpl in cls.get_templates():
            if tpl.get_id() == id_:
                return tpl

    @classmethod
    def success(cls, text, newline=True):
        type_txt = 'Success'.ljust(cls.LOG_TYPE_SIZE)
        sys.stdout.write('{0} |  {1}'.format(
            ColoredString(type_txt, bcolors.OKGREEN), text))
        if newline:
            sys.stdout.write('\n')
        sys.stdout.flush()

    @classmethod
    def notice(cls, text, newline=True):
        type_txt = 'Notice'.ljust(cls.LOG_TYPE_SIZE)
        sys.stdout.write('{0} |  {1}'.format(
            ColoredString(type_txt, bcolors.WARNING), text))
        if newline:
            sys.stdout.write('\n')
        sys.stdout.flush()

    @classmethod
    def info(cls, text, newline=True):
        type_txt = 'Info'.ljust(cls.LOG_TYPE_SIZE)
        sys.stdout.write('{0} |  {1}'.format(
            ColoredString(type_txt, bcolors.OKGREEN), text))
        if newline:
            sys.stdout.write('\n')
        sys.stdout.flush()

    @classmethod
    def fatal(cls, text=None):
        type_txt = 'Fatal'.ljust(cls.LOG_TYPE_SIZE)
        if text:
            print('{0} |  {1}'.format(
                ColoredString(type_txt, bcolors.FAIL), text))
        sys.exit(1)


App.init()

ETC_TEMPLATES = App.ETC + '/templates/*.yml'
