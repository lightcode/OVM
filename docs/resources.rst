Configure resources
===================

Resources are configured in the YAML file ``resources.yml``. This file
follow the YAML syntax and there are two mains dictionaries: ``storage``
and ``networks``. Each dictionary is described in this chapter.



Storage pools
-------------

Storage pools are used by OVM to create the disk of VMs. To add a new
storage pool, we add a dictionary where the key is the **pool name**.
This dictionary contains another dictionary with parameters.

There are two commons parameters, there are not optional :

**driver**
   is the name of the storage driver. OVM uses it, when you
   create your VMs, to create disks.
**root**
   this parameter specifies the root of the pool. Note: don’t
   create several storage pools with the same ``root`` path.

Currently, there are two drivers as you can see below.



The file driver
~~~~~~~~~~~~~~~

To use flat file to store VM disks.


**File driver additional parameters**:

**disk_format**
   define the format of the disk file.

   Supported values: qcow2, raw. (Default: qcow2)


**Configuration example**:

.. code-block:: yaml

    storage:
      ssd:
        driver: file
        root: /mnt/pool-vm-ssd
        disk_format: qcow2

Here we create the storage pool **ssd**. We use the driver **file** to
access it.




The LVM driver
~~~~~~~~~~~~~~

To use a LVM volume group to store VM disks. OVM create automatically
one logical volume per disk. You have to create the volume group
yourself. For example:

.. code-block:: console

    # vgcreate OVM_VG /dev/sda /dev/sdb


**Configuration example**:

.. code-block:: yaml

   storage:
     lvm:
       driver: lvm
       root: /dev/OVM_VG
       volume_group: OVM_VG


Here we create the storage pool **lvm**. We use the driver **lvm**. We
need to specify the `root`, with LVM it is the path to the volume group.
The third parameter is the name of the volume group (`volume_group`).



Networks
--------


Networks are used by OVM to add an interface in the VM and eventually to
configure the IP stack. To add a new network, we add a dictionary where
the key is the **Network ID**. This dictionary contains another dictionary
with different parameters:

**driver**
   is the name of the network driver. OVM uses it to create new VMs
   with the right configuration. Today, only the driver
   `bridge` exists.
**bridge**
   is the name of the bridge on your hypervisor.
**vlan**
   is the VLAN ID used by your network.
   *This option is facultative*. Default: not set (no VLAN created).
**openvswitch**
   if your bridge is an Open vSwitch bridge, then put this parameter at true.
   *This option is facultative*. Default: `false`.
**ipv4_allocation**
   this parameter is used to precise to OVM the type of IPv4 allocation.
   You can choose `static` and precise the `ipv4_pool` parameter or you
   can choose `dhcp` and let the DHCP server on your network allocate the IPv4.
**ipv4_pool**
   it's a set of parameters to configure the IP allocation.

**Configuration example**:

.. code-block:: yaml

   networks:
     local:
       driver: bridge
       openvswitch: true
       bridge: sw0
       vlan: 42
       ipv4_allocation: static
       ipv4_pool:
         ip_start: 192.168.1.30
         ip_end: 192.168.1.63
         netmask: 24
         gateway: 192.168.1.1
         nameservers: ['192.168.1.1']
