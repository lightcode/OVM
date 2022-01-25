#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__all__ = ["OVMError", "DomainException", "DriverError"]


class OVMError(Exception):
    def __init__(self, message):
        super(OVMError, self).__init__(message)
        self.message = message


class DomainException(OVMError):
    pass


class DriverError(OVMError):
    pass
