#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from lxml import etree
except ImportError:
    try:
        import xml.etree.cElementTree as etree
    except ImportError:
        import xml.etree.ElementTree as etree

__all__ = ["etree"]
