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


class Volume(object):

    def __init__(self, storage, diskpath, target):
        self._storage_pool = storage
        self._driver = storage.get_device(diskpath)
        self.path = diskpath
        self.pool_name = storage.name
        self.target = target

    def remove(self):
        self._driver.remove()

    @property
    def capacity(self):
        return self._driver.capacity

    @property
    def allocated(self):
        return self._driver.allocated
