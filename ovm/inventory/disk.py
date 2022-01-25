#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ovm.exceptions import OVMError
from ovm.utils.compat23 import etree


class Disk:
    def __init__(self, **kargs):
        self.guest_dev = None

        if "xmldef" in kargs:
            xmldef = kargs["xmldef"]

            disk_type = xmldef.attrib.get("type")
            if disk_type not in ("file", "block"):
                raise OVMError("Unknown disk type.")

            source = xmldef.find("source")
            if source is None:
                raise OVMError("Source is missing on the libvirt device.")

            disk_path_attr = dict(file="file", block="dev").get(disk_type)
            disk_path = source.attrib.get(disk_path_attr)

            target = xmldef.find("target")
            if target is not None:
                self.guest_dev = str(target.attrib.get("dev"))

            from ovm.resources.resources import Resources

            storage_pool = None
            for storage in Resources.get_storage_pools():
                if disk_path.startswith(storage.root):
                    storage_pool = storage
                    break

            if storage_pool is None:
                raise OVMError("Cannot find storage pool.")

            driver = storage_pool.driver

        elif "storage_pool" in kargs and "name" in kargs:
            storage_pool = kargs["storage_pool"]
            driver = storage_pool.driver

            template_params = kargs.get("template_params", dict())
            name = str(kargs["name"])
            image = template_params.get("image")
            self._template_params = template_params
            disk_path = driver.import_image(image, name)

        else:
            raise OVMError("Not enough arguments are passed to Disk.")

        self.path = disk_path
        self.pool = storage_pool
        self._driver = driver

    @property
    def xml_definition(self):
        if not self._template_params:
            raise NotImplementedError("Cannot get xml definition without creation")

        target = etree.Element("target")
        target.attrib["dev"] = self._template_params.get("target_dev")
        target.attrib["bus"] = self._template_params.get("target_bus")
        xmldef = self._driver.generate_xml(self)
        xmldef.append(target)

        return etree.tostring(xmldef).decode("utf-8")

    def resize(self, new_size):
        self._driver.resize_disk(self, new_size)

    def remove(self):
        self._driver.remove_disk(self)

    @property
    def size(self):
        return self._driver.disk_real_size(self)
