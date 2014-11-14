OVM (Open Virtualization Manager) is a tool that allows you to create and manage VMs. This version of OVM can handle the hypervisor KVM with libvirt. The tool must be run directly on the hypervisor.

This tool is delivering with few drivers to handle networks and storage system but you can build easily your own scripts.


# Installation

This project use Python 3, you can install it on Debian with this command:

    # apt-get install python3


You also need to install these packages on your hypervisor:

* libvirt
* python3-libvirt

You can simply use your package manager or build them yourself.

**Note**: libvirt must have volume and Qemu metadata support.


We need to install Python libraries (example on Debian):

    # apt-get install python3-lxml python3-ipaddr python3-yaml

Now, you can download and extract OVM. Then, to achieve the installation, we simply do this command into the `ovm` directory:

    # python3 setup.py install


# Commands

OVM is used with the command `vm`. This command take a subcommand like this `vm start <name_of_vm>`.


Subcommand    | Description
------------- | -------------------------------------------------
console       | Open a console on the VM
create        | Create a VM
info          | Give information about a VM
ls (list)     | Print the list of VM
networks      | Print the list of networks
ping          | Shortcut to ping a VM with the static IP
reboot        | Reboot a VM
rm (remove)   | Remove a VM
set           | Modify some properties of VM
ssh           | Shortcut to open a SSH session on the VM
start         | Start a VM
stop          | Halt a VM gracefully
storages      | Print the list of storages
templates     | Print the list of templates

**Notes**:

* The `ssh` and `ping` are usable if an IP address is set into the VM
* The metadata `backup` that you can change with the command `set` is useless but, you can create your own script that use this metadata. You can list all backed machine with the command `vm list --short --backup`.


# Configure OS templates

To use the template, you must modify parameters in the YAML file. OVM is distributing with some templates you must configure and create the images. You must edit the path to the disk in the file:

```yaml
main_disk:
  path: /mnt/pool-templates/debian-wheezy.qcow2
```

If you want to handle another OS by OVM, you need to create a new template. A template is a YAML file we create in the folder `/etc/templates`. You can look at the existing templates to build another one.


# Configure resources

The resources are configure in the YAML file `resources.yml`. The file follow the YAML syntax and there are two main dictionaries: `storages` and `networks`. Each dictionary is described in this chapter.


## Storage pools

Storage pools are used by OVM to create the disk of VMs. To add a new storage pool, we add a dictionary where the key is the **Pool ID**. This dictionary contains another dictionary with different parameters:

* **driver**: this key tells to OVM how to handle the pool. Today, only the driver `VolumeDriver` exists.
* **pool_name**: this parameter specifies the name of the pool in libvirt.

**Example**:

```yaml
storages:
  ssd:
    driver: VolumeDriver
    pool_name: pool-vm-ssd
```

Here we create the storage pool *ssd*. We use the driver *VolumeDriver* to access it. The other parameter, _pool-vm-ssd_ is the name of the libvirt pool.


## Networks

Networks are used by OVM to add an interface in the VM and eventually to configure the IP stack. To add a new network, we add a dictionary where the key is the **Network ID**. This dictionary contains another dictionary with different parameters:

* **driver**: this key tells to OVM how to handle the network. Today, only the driver `OpenvSwitchDriver` exists.
* **net_name**: the parameter `net_name` define the name of the network in libvirt.
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
