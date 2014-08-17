OVM (Open Virtualization Manager) is a tool that allows you to create and manage VMs. This version of OVM can handle the hypervisor KVM with libvirt. The tool must be run directly on the hypervisor.

This tool is delivering with few drivers to handle networks and storage system but you can build easily your own scripts.


# Installation

First of all, you need to install this package on your hypervisor:

* libvirt
* python-libvirt

You can simply use your package manager or build from scratch.

*Note*: libvirt must have volume and Qemu metadata support.


We need to install Python libraries (example on Debian):

    # apt-get install python-pip python-lxml
    # pip install ipaddr

Then, to achieve the installation, we simply do this command:

    # python setup.py install


# Commands

OVM is used with the command `vm`. This command take a subcommand like this `vm start <name_of_vm>`.


Subcommand    | Description
------------- | -------------------------------------------------
create        | Create a VM
info          | Give information about a VM
list          | Print the list of VM
networks      | Print the list of networks
ping          | Shortcut to ping a VM with the static IP
reboot        | Reboot a VM
remove        | Remove a VM
set           | Modify some properties of VM
ssh           | Shortcut to open a SSH session on the VM
start         | Start a VM
stop          | Halt a VM gracefully
storages      | Print the list of storages
templates     | Print the list of templates

*Notes*:

* The `ssh` and `ping` are usable if an IP address is set into the VM
* The metadata `backup` that you can change with the command `set` is useless but, you can create your own script that use this metadata. You can list all backed machine with the command `vm list --short --backup`.


# Configure OS templates

To use the template, you must modify parameters in the JSON file. OVM is distributing with some templates you must configure and create the images. You must edit the path to the disk in the file:

```json
{
  "main_disk": {
    "path": "/var/kvm/storage/pool-templates/debian-wheezy.qcow2"
  }
}
```

If you want to handle another OS by OVM, you need to create a new template. A template is a JSON file we create in the folder `/etc/templates`. You can look at the existing templates to build another one.


# Configure resources

## Storage pools

The storage pool is used by OVM to create the disk of VMs. To add a new storage pool, add the following line at the end of the bloc "Storage pools definition" in `config.py`:

```python
STORAGES['ssd'] = VMStorage(
    VolumeDriver,
    pool_name='pool-vm-ssd')
```

Explanations:

* *Pool name*: the name of the book is given by the name in hooks (here: ssd)
* *Driver* : it’s a Python class that permit to OVM to handle resources. Here the driver allow to OVM to use a libvirt pool
* *pool_name* is a driver specific parameter and it specifies the name of the libvirt pool


## Networks

To add a network connection to a VM, you must create a network. The network can be used to configure a static IPv4 automatically.

You can add network by adding the following line at the end of the bloc "Networks definition" in `config.py` :


```python
NETWORKS['local'] = VMNetwork(
    OpenvSwitchDriver,
    bridge_name='net-ovs',
    net_portgroup='local',
    pool_ip={
        'ip_start': '192.168.1.30',
        'ip_end': '192.168.1.63',
        'netmask': 24,
        'gateway': '192.168.1.1',
        'nameservers': ['192.168.1.1'],
        'autoip_path': '/var/kvm/scripts/vm/.app/local.net'
    }
)
```


Explanations:

* *Network name*: the name in the hook at the first line, it’s the name of the network we use in OVM
* *Driver*: permit to OVM to handle the resource. Here the driver allow to OVM to use a libvirt network
* *bridge_name*: it’s the name of the network in libvirt
* *net_portgroup*: it’s the name of the portgroup (virtual network defined in libvirt)
* *pool_ip*: it's a set of parameters to configure the IP allocation
