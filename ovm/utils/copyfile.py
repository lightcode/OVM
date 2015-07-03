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


import concurrent.futures
import os
import shutil
import sys
import time


class CopyFile:
    def __init__(self, text=''):
        self.text = text
        self.pattern = '{0} [{1}%]'
        sys.stdout.write('\n')
        sys.stdout.flush()

    def _monitor(self, src, dst):
        src_size = 0
        dst_size = 1
        while src_size != dst_size:
            src_size = os.path.getsize(src)
            dst_size = os.path.getsize(dst)
            self._update_progress_bar(dst_size, src_size)
            time.sleep(1)

    def copy_progress(self, src, dst):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            threads = []
            threads.append(executor.submit(shutil.copyfile, src, dst))
            threads.append(executor.submit(self._monitor, src, dst))
            for future in concurrent.futures.as_completed(threads):
                if future.exception() is not None:
                    print(future.exception())
        sys.stdout.write('\n')
        sys.stdout.flush()

    def _update_progress_bar(self, cur, total):
        percent = int((cur / total) * 100)
        text = self.pattern.format(self.text, percent)
        sys.stdout.write('\r' + text)
        sys.stdout.flush()
