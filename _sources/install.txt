Installation
============

This project use Python 3, you can install it on Debian with this
command:

.. code-block:: console

    # apt-get install python3

You also need to install these packages on your hypervisor:

-  libvirt
-  python3-libvirt
-  guestfish

You can simply use your package manager or build them yourself.

**Note**: libvirt must have volume and Qemu metadata support.

We need to install Python libraries (example on Debian):

.. code-block:: console

    # apt-get install python3-pip


Now, you can download and extract OVM. Then, to achieve the
installation, we simply do this command into the ``ovm`` directory:

.. code-block:: console

    # python3 setup.py install
