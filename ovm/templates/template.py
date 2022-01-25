#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os.path
import yaml

from ovm.configuration import Configuration
from ovm.exceptions import OVMError
from ovm.templates.image_template import ImageTemplate


class Template:
    TEMPLATES_PATH = Configuration.ETC_TEMPLATES
    DEFAULT_VCPU = 1
    DEFAULT_MEMORY = 256
    DEFAULT_ABILITIES = {"resizeDisk": False}

    _templates_cache = None

    def __init__(self, config):
        self.uid = config.get("uid")
        self.name = config.get("name")
        self.vcpu = int(config.get("vcpu", Template.DEFAULT_VCPU))
        self.memory = int(config.get("memory", Template.DEFAULT_MEMORY))
        self.metadata = dict(config.get("metadata", {}))
        self.main_interface = dict(config.get("main_interface", {}))
        self.post_install = list(config.get("post_install", []))

        self._process_main_disk(config)

        abilities = Template.DEFAULT_ABILITIES.copy()
        abilities.update(config.get("abilities", {}))
        self.abilities = abilities

    def __repr__(self):
        return "<Template uid={0.uid}>".format(self)

    def _process_main_disk(self, config):
        main_disk = dict(config.get("main_disk", {}))
        image_config = dict(main_disk.get("image", {}))
        main_disk["image"] = ImageTemplate(image_config)
        self.main_disk = main_disk

    def get_os_type(self):
        return self.metadata.get("os_type")

    def get_os_name(self):
        return self.metadata.get("os_name")

    def get_os_version(self):
        return self.metadata.get("os_version")

    @classmethod
    def load_from_file(cls, path):
        try:
            with open(path, "r") as fd:
                config = yaml.load(fd.read())
                return cls(config)
        except IOError as err:
            raise OVMError('Template "{0}" cannot be load: {1}.'.format(path, err))

    @classmethod
    def _load_templates(cls):
        templates = {}
        for path in glob.iglob(os.path.join(cls.TEMPLATES_PATH, "*.yml")):
            template = cls.load_from_file(path)
            templates[template.uid] = template

        cls._templates_cache = templates

    @classmethod
    def get_templates(cls):
        if cls._templates_cache is None:
            cls._load_templates()

        return list(cls._templates_cache.values())

    @classmethod
    def get_template(cls, uid):
        if cls._templates_cache is None:
            cls._load_templates()

        try:
            return cls._templates_cache[uid]
        except KeyError:
            raise OVMError('Template "{0}" not found.'.format(uid))
