:warning: **This project is not maintained anymore.**

---

# Open Virtualization Manager (OVM)

OVM is a software tool designed for managing KVM virtual machines. It facilitates the lifecycle management of virtual machines including starting, stopping, and rebooting. This program provides a feature for creating VMs based on customizable templates. Additionally, it relies on a resource file for defining existing networks and storage pools on a machine. OVM also offers higher-level functions such as SSH connection to a VM or performing a ping.

<p align="center">
  <img src="/docs/images/screenshot.png?raw=true" alt="Screenshot"/>
</p>

## Overview

OVM adds a new command named simply `vm`, followed by a keyword defining the action to be performed. For example:

```console
$ vm create example --storage hdd --network prod --template debian-wheezy
```

This command creates a VM named "example" based on the "debian-wheezy" template, utilizing the storage pool named "hdd" and the "prod" network. The `vm ls` command lists the created VMs. For more information on available commands, you can type `vm -h` or visit the project page.

## Development

Follow the [install documentation](/docs/install.rst) to setup your environment.

Run tests:

```console
$ python3 tests/main.py
```
