#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
from setuptools import setup, find_packages

from ovm.configuration import Configuration


setup(
    name="OVM",
    version=Configuration.VERSION,
    description="Open Virtualization Manager",
    author="lightcode",
    url="http://lightcode.fr",
    install_requires=["pyaml==5.4.1", "sphinx=7.2.6"],
    packages=find_packages(),
    data_files=[("bash_completion.d", ["bin/vm-completion"])],
    entry_points={"console_scripts": ["vm = ovm.vmcli.__main__:main"]},
)

if not os.path.exists(Configuration.ETC):
    shutil.copytree("etc/", Configuration.ETC)

if not os.path.exists(Configuration.SAVED_VMS):
    os.makedirs(Configuration.SAVED_VMS)
