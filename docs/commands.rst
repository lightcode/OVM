Command reference
=================

OVM includes the command ``vm``. This command take a subcommand like
this ``vm start...`` or ``vm create...``.


Here, you have the list of subcommands:

.. option:: autostart

   Choose if the VM starts automatically at boot


.. option:: console

   Open a console on the VM.

   To close the connection, you have to press ``Ctrl+]`` or ``Ctrl+5``.

   See :ref:`configure-serial`.


.. option:: create

   Create a VM


.. option:: info

   Give information about a VM


.. option:: ls

   Print the list of VM


.. option:: networks

   Print the list of networks


.. option:: ping

   Shortcut to ping a VM with the static IP

   Important: this command only works if you have fixed an IP address on the VM.


.. option:: reboot

   Reboot a VM


.. option:: restore

   Restore a VM


.. option:: rm

   Remove a VM


.. option:: save

   Save a VM


.. option:: set

   Edit VM's metadata entries.

   You can edit several metadata items in one command: ``vm set vmname os_type=linux os_name=Debian os_version=7``.


.. option:: ssh

   Shortcut to open a SSH session on the VM

   Important: this command only works if you have fixed an IP address on the VM.


.. option:: start

   Start a VM


.. option:: stop

   Halt a VM gracefully


.. option:: storage

   Print the list of storage


.. option:: templates

   Print the list of templates


.. option:: top

   Show live stats about VMs


.. option:: unset

   Remove VM's metadata entries.

   You can remove several metadata entries in one command: ``vm unset vmname os_type os_name os_version``.
