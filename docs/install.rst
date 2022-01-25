Installation
============

This project requires ``pip``, ``libvirt`` and ``guestfish`` installed on your system:

.. code-block:: console

    $ sudo apt-get install --no-install-recommends guestfish libvirt-daemon-system python3-libvirt python3-pip
    $ sudo systemctl enable --now libvirtd
    $ sudo usermod -aG kvm $USER
    $ sudo usermod -aG libvirt $USER

**Note**: libvirt must have volume and Qemu metadata support.

Install it in a virtualenv:

.. code-block:: console

    $ python3 -m venv --system-site-packages .venv
    $ source .venv/bin/activate
    $ python3 setup.py install
