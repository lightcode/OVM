#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from abc import ABCMeta


class Driver(metaclass=ABCMeta):
    def __init__(self):
        self._params = {}

    def set_params(self, **kargs):
        self._params.update(kargs)
