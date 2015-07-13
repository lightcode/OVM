#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
                    sys.stdout.write(future.exception())
                    sys.stdout.flush()
        sys.stdout.write('\n')
        sys.stdout.flush()

    def _update_progress_bar(self, cur, total):
        percent = int((cur / total) * 100)
        text = self.pattern.format(self.text, percent)
        sys.stdout.write('\r' + text)
        sys.stdout.flush()
