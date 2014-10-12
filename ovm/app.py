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


import sys
from glob import iglob
from ovm.template import Template


class Singleton(object):
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance


class App(Singleton):
    templates = []
    _templates_loaded = False
    ETC = '/etc/ovm'

    @classmethod
    def init(cls):
        pass

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
    def fatal(cls, text=None):
        if text:
            print(text, file=sys.stderr)
        sys.exit(1)


App.init()

ETC_TEMPLATES = App.ETC + '/templates/*.yml'
