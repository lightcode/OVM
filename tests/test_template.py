#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os.path
import unittest

from ovm.exceptions import OVMError
from ovm.templates.template import Template


ROOT = os.path.dirname(os.path.realpath(__file__))
TEMPLATES_PATH = os.path.abspath(os.path.join(ROOT, "../etc/templates/examples"))


# Configure for looking into local etc/templates/examples
Template.TEMPLATES_PATH = TEMPLATES_PATH


class TestTemplate(unittest.TestCase):
    def test_get_templates(self):
        """get_tempaltes should load all templates and return them all"""
        template_count = len(glob.glob(os.path.join(TEMPLATES_PATH, "*.yml")))
        templates = Template.get_templates()
        self.assertEqual(template_count, len(templates))

    def test_get_a_specific_template(self):
        """get_template should return the correct template"""
        uid_list = ("centos-7", "debian-8")
        for uid in uid_list:
            template = Template.get_template(uid)
            self.assertEqual(uid, template.uid)

    def test_get_an_unknown_template(self):
        """get_template should raise an OVMError"""
        with self.assertRaises(OVMError):
            Template.get_template("an-unknown-template")
