#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
from subprocess import PIPE

from ovm.drivers.storage.generic import StorageDriver
from ovm.exceptions import DriverError
from ovm.utils.logger import logger
from ovm.utils.compat23 import Popen, etree


__all__ = ["LvmDriver"]


class LvmDriver(StorageDriver):
    DISK_FORMAT = "raw"

    def __init__(self):
        super(LvmDriver, self).__init__()

    def _create_logical_volume(self, name, size):
        size = "{}G".format(size)
        vgname = self._params.get("volume_group")

        if not vgname:
            DriverError("Volume Groupe not set.")

        args = ["lvcreate", "--size", size, "--name", str(name), vgname]
        with Popen(args, stdout=PIPE, stderr=PIPE) as process:
            process.wait()
            if process.returncode != 0:
                DriverError(process.stderr.read().decode("utf-8"))

    def generate_xml(self, disk):
        disktree = etree.Element("disk")
        disktree.set("type", "block")
        disktree.set("device", "disk")

        driver = etree.SubElement(disktree, "driver")
        driver.set("name", "qemu")
        driver.set("type", LvmDriver.DISK_FORMAT)
        driver.set("cache", "writeback")

        source = etree.SubElement(disktree, "source")
        source.set("dev", disk.path)

        return disktree

    def resize_disk(self, disk, new_size):
        args = ["lvresize", "--size", "{}G".format(new_size), disk.path]
        with Popen(args, stdout=PIPE, stderr=PIPE) as process:
            process.wait()
            if process.returncode != 0:
                DriverError(process.stderr.read().decode("utf-8"))

    def import_image(self, image, name):
        path = os.path.join(self._params.get("root"), name)
        self._create_logical_volume(name, image.size)

        if not os.path.exists(path):
            raise DriverError("Volume group not created.")

        image.copy_on_device(path, LvmDriver.DISK_FORMAT)

        return path

    def remove_disk(self, disk):
        logger.debug('Trying to remove disk "%s".', disk.path)
        args = ["lvremove", "--force", disk.path]
        with Popen(args, stdout=PIPE, stderr=PIPE) as process:
            process.wait()
            if process.returncode != 0:
                DriverError(process.stderr.read().decode("utf-8"))
