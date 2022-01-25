#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import libvirt

from ovm.utils.logger import logger


class LibvirtConnect:
    _conn = None
    _connection_string = "qemu:///system"

    @classmethod
    def get_connection(cls):
        if cls._conn is None:
            cls._conn = libvirt.open(cls._connection_string)
            logger.debug("New connection to libvirt opened.")
        return cls._conn
