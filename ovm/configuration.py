#!/usr/bin/env python3

import os.path


__all__ = ['Configuration']


class Configuration:

    VERSION = '0.2'
    ETC = '/etc/ovm'
    SAVED_VMS = '/var/lib/ovm/saved-vms'
    ETC_TEMPLATES = ETC + '/templates'
    RESOURCE_CONFIG = os.path.join(ETC, 'resources.yml')
