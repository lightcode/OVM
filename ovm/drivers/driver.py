#!/usr/bin/env python3


class Driver:

    def __init__(self):
        self._params = {}

    def set_params(self, **kargs):
        self._params.update(kargs)
