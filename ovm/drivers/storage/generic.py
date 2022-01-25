#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from abc import abstractmethod

from ovm.drivers.driver import Driver


class StorageDriver(Driver):
    @abstractmethod
    def generate_xml(self, disk):
        pass

    @abstractmethod
    def resize_disk(self, disk, new_size):
        pass

    @abstractmethod
    def remove_disk(self, disk):
        pass

    @abstractmethod
    def import_image(self, image, name):
        pass

    def disk_real_size(self, disk):
        """Get the file size by seeking at end"""
        try:
            fd = os.open(disk.path, os.O_RDONLY)
        except OSError:
            return 0

        try:
            size = os.lseek(fd, 0, os.SEEK_END)
        finally:
            os.close(fd)
            return size
