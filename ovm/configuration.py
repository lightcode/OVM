#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path


__all__ = ["Configuration"]


ROOT = os.path.join(os.path.expanduser("~"), "ovm")


class Configuration:
    VERSION = "0.4"
    ETC = os.path.join(ROOT, "etc")
    VAR = os.path.join(ROOT, "var")

    RESOURCE_CONFIG = os.path.join(ETC, "resources.yml")
    ETC_TEMPLATES = os.path.join(ETC, "templates")

    SAVED_VMS = os.path.join(VAR, "saved-vms")
    IP_DATABASE = os.path.join(VAR, "ipdatabase.db")
