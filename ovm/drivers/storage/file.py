#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
from subprocess import PIPE

from ovm.drivers.storage.generic import StorageDriver
from ovm.exceptions import DriverError
from ovm.utils.logger import logger
from ovm.utils.compat23 import Popen, etree


__all__ = ["FileDriver"]


class FileDriver(StorageDriver):
    def __init__(self):
        super(FileDriver, self).__init__()
        self._params = {"disk_format": "qcow2"}

    def set_params(self, **params):
        if "disk_format" in params:
            disk_format = str(params["disk_format"])
            if disk_format not in ("raw", "qcow2"):
                raise DriverError("Disk format not supported")
            params["disk_format"] = disk_format

        super(FileDriver, self).set_params(**params)

    def generate_xml(self, disk):
        disktree = etree.Element("disk")
        disktree.set("type", "file")
        disktree.set("device", "disk")

        driver = etree.SubElement(disktree, "driver")
        driver.set("name", "qemu")
        driver.set("type", self._params["disk_format"])
        driver.set("cache", "writeback")

        source = etree.SubElement(disktree, "source")
        source.set("file", disk.path)

        return disktree

    def resize_disk(self, disk, new_size):
        if not os.path.exists(disk.path):
            raise DriverError('Path "{0}" does not exists'.format(disk.path))

        args = ["qemu-img", "resize", disk.path, "{}G".format(new_size)]
        with Popen(args, stdout=PIPE, stderr=PIPE) as process:
            process.wait()
            if process.returncode != 0:
                raise DriverError(process.stderr.read().decode("utf-8"))

    def import_image(self, image, name):
        path = os.path.join(self._params.get("root"), name)
        try:
            fd = open(path, "w+")
        finally:
            fd.close()
        image.copy_on_device(path, self._params["disk_format"])
        return path

    def remove_disk(self, disk):
        logger.debug('Trying to remove disk "%s".', disk.path)
        try:
            os.remove(disk.path)
        except OSError as err:
            raise DriverError('Cannot remove disk "{}": {}'.format(disk.path, err))
