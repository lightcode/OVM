#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from threading import Thread
import os
import sys
import time


# Control code VT100 to erase a line
ERASE_LINE = "\x1b[2K"


class CopyProgress(Thread):
    def __init__(self, src, dst, text=""):
        super(CopyProgress, self).__init__()

        self._is_stopped = False
        self.source_size = os.path.getsize(src)
        self.destination = dst
        self.pattern = " ".join((text, "[{0}%]"))
        self.output = sys.stderr

    def run(self):
        # Don't do anything if we are not in a TTY
        if not self.output.isatty():
            return

        while not self._is_stopped:
            dst_size = os.path.getsize(self.destination)
            self._update_progress_bar(dst_size, self.source_size)
            time.sleep(1)

        # Erase line with VT100 control code
        self.output.write("\r" + ERASE_LINE)
        self.output.flush()

    def finish(self):
        self._is_stopped = True

        if self.is_alive():
            self.join()

    def _update_progress_bar(self, cur, total):
        percent = int((cur * 100) / total)
        text = "\r" + self.pattern.format(percent)
        self.output.write("\r" + text)
        self.output.flush()
