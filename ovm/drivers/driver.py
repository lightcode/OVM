#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from six import with_metaclass

from abc import ABCMeta


class Driver(with_metaclass(ABCMeta)):

    def __init__(self):
        self._params = {}

    def set_params(self, **kargs):
        self._params.update(kargs)
