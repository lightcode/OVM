#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import sys
import os


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(1, ROOT)


from test_driver_loader import TestDriverLoader         # noqa
from test_resource_loader import TestResourceLoader     # noqa
from test_template import TestTemplate                  # noqa


if __name__ == '__main__':
    unittest.main()
