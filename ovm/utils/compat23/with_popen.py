#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from subprocess import Popen


__all__ = ["Popen"]


class WithPopen(Popen):
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.stdout:
            self.stdout.close()
        if self.stderr:
            self.stderr.close()
        try:  # Flushing a BufferedWriter may raise an error
            if self.stdin:
                self.stdin.close()
        finally:
            # Wait for the process to terminate, to avoid zombies.
            self.wait()


if not hasattr(Popen, "__exit__"):
    Popen = WithPopen
