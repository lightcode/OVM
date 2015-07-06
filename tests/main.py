import unittest
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(1, ROOT)


# flake8: noqa
from test_driver_loader import TestDriverLoader
from test_resource_loader import TestResourceLoader


if __name__ == '__main__':
    unittest.main()
