OVM (Open Virtualization Manager) is a tool that allows you to create and manage VMs. This version of OVM can handle the hypervisor KVM with libvirt. This tool must run directly on the hypervisor.

This tool is delivering with few drivers to handle networks and storage system but you can build easily your own scripts.


# Installation

This project use Python 3, you can install it on Debian with this command:

    # apt-get install python3


You also need to install these packages on your hypervisor:

* libvirt
* python3-libvirt
* guestfish

You can simply use your package manager or build them yourself.

**Note**: libvirt must have volume and Qemu metadata support.


We need to install Python libraries (example on Debian):

    # apt-get install python3-lxml python3-ipaddr python3-pip


We need to install all requirements with pip:

    # pip-3.2 install -r requirements.txt


Now, you can download and extract OVM. Then, to achieve the installation, we simply do this command into the `ovm` directory:

    # python3 setup.py install


# Commands

OVM includes the command `vm`. This command take a subcommand like this `vm start...` or `vm create...`. You can find the commands list in the page [Commands](doc/commands.md) in the documentation.


# Configure OS templates

You can create your own templates based on those given in the `/etc/ovm/templates/examples`. In this case, you must modify parameters in the YAML file. For example, you have to edit the path to the disk in the file:

```yaml
main_disk:
  path: /mnt/pool-templates/debian-wheezy.qcow2
```

Templates are stored into the `/etc/ovm/templates` directory. Templates names have to end with `.yml` extension.


# Configure resources

Resources are configured in the YAML file `resources.yml`. This file follow the YAML syntax and there are two mains dictionaries: `storage` and `networks`. Each dictionary is described in this chapter.


## Storage pools

Storage pools are used by OVM to create the disk of VMs. To add a new storage pool, we add a dictionary where the key is the **pool name**. This dictionary contains another dictionary with different parameters:

* **driver**: is the name of the storage driver. OVM uses it, when you create your VMs, to create disks.
* **root**: this parameter specifies the root of the pool. Note: don't create several storage pools with the same @root@ path.

**Example**:

```yaml
storage:
  ssd:
    driver: FileDriver
    root: /mnt/pool-vm-ssd
```

Here we create the storage pool *ssd*. We use the driver *FileDriver* to access it.


## Networks

Networks are used by OVM to add an interface in the VM and eventually to configure the IP stack. To add a new network, we add a dictionary where the key is the **Network ID**. This dictionary contains another dictionary with different parameters:

* **driver**: is the name of the network driver. OVM uses it to create new VMs with the right configuration. Today, only the driver `OpenvSwitchDriver` exists.
* **net_name**: the parameter `net_name` defines the name of the network in libvirt.
* **net_portgroup**: this term is used in libvirt configuration network. _This option is facultative_.
* **ipv4_allocation**: this parameter is used to precise to OVM the type of IPv4 allocation. You can choose `static` and precise the `ipv4_pool` parameter or you can choose `dhcp` and let the DHCP server on your network allocate the IPv4.
* **ipv4_pool**: it's a set of parameters to configure the IP allocation.

**Example**:

```yaml
networks:
  local:
    driver: OpenvSwitchDriver
    net_name: net-ovs
    net_portgroup: local
    ipv4_allocation: static
    ipv4_pool:
      ip_start: 192.168.1.30
      ip_end: 192.168.1.63
      netmask: 24
      gateway: 192.168.1.1
      nameservers: ['192.168.1.1']
      autoip_path: /etc/autoip/ovm/local.dat
```
