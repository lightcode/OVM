#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from subprocess import PIPE

from ovm.exceptions import OVMError
from ovm.utils.compat23 import Popen
from ovm.utils.copyprogress import CopyProgress


class ImageTemplate:
    def __init__(self, config):
        self.path = config.get("path")
        self.format = config.get("format")
        self.size = int(config.get("size"))

    def copy_on_device(self, dest, dest_format):
        if not os.path.exists(dest):
            raise OVMError("copy_on_device: destination must exists.")

        cp = CopyProgress(self.path, dest, "Copy image file")
        cp.start()

        args = [
            "qemu-img",
            "convert",
            "-f",
            str(self.format),
            "-O",
            str(dest_format),
            self.path,
            dest,
        ]

        with Popen(args, stderr=PIPE) as process:
            process.wait()
            if process.returncode != 0:
                raise OVMError(process.stderr.read().decode("utf-8"))

        cp.finish()
