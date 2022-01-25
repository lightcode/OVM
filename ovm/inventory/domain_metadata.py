#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import libvirt
import xml.etree.ElementTree as ET


class DomainMetadata:
    def __init__(self, domain):
        self._metadata = {}
        self._domain = domain

        try:
            xml = domain.metadata(
                libvirt.VIR_DOMAIN_METADATA_ELEMENT,
                "uri://ovm",
                libvirt.VIR_DOMAIN_XML_INACTIVE,
            )
        except libvirt.libvirtError:
            pass
        else:
            root = ET.fromstring(xml)
            for element in root.findall("entry"):
                name = element.get("name")
                value = element.get("value")
                if name is not None:
                    self._metadata[name] = value

    def __iter__(self):
        for name, value in self._metadata.items():
            yield (name, value)

    def __getitem__(self, key):
        return self._metadata.get(str(key).lower())

    def __setitem__(self, key, value):
        self._metadata[str(key).lower()] = str(value)

    def __delitem__(self, key):
        del self._metadata[str(key)]

    def get(self, name):
        return self._metadata.get(str(name).lower())

    def update(self, entries=None, **kargs):
        if type(entries) is dict:
            kargs.update(entries)

        for name, value in kargs.items():
            name = str(name).lower()
            self._metadata[name] = str(value)
        self.save()

    def save(self):
        root = ET.Element("metadata")

        for name, value in self._metadata.items():
            entry = ET.SubElement(root, "entry")
            entry.set("name", name)
            entry.set("value", value)

        xml = ET.tostring(root).decode("utf8")
        self._domain.setMetadata(
            libvirt.VIR_DOMAIN_METADATA_ELEMENT,
            xml,
            "ovm",
            "uri://ovm",
            libvirt.VIR_DOMAIN_XML_INACTIVE,
        )
