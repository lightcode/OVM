#!/usr/bin/env python3

import os

from ovm.drivers.driver import Driver


class StorageDriver(Driver):

    def disk_real_size(self, disk):
        "Get the file size by seeking at end"
        try:
            with open(disk.path, 'rb') as fd:
                return fd.seek(0, os.SEEK_END)
        finally:
            pass
