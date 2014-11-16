OVM commands
============

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

* The `ssh` and `ping` work if you set an IP address on the VM



## `vm console`

Open a console on the VM.

Syntax: 

    vm console [-h] name

To close the connection, you have to press `Ctrl+]` or `Ctrl+5`.

Read also [Configure a serial console on your VM](console.md).



## `vm set`

Modify some properties of VM.

Syntax: 

    vm set [-h] [--backup {on,off}]
                [--starting {auto,manual}]
                [--ip IP] [--os-type OS_TYPE]
                [--os-name OS_NAME]
                [--os-version OS_VERSION]
                name

Parameters:

* `--backup {on,off}` : this option allows you to change the _backup_ metadata. This metadata is usefull only if you want to store which VM you back up with your own script. OVM doesn't back up nothing. You can list all backed machine with the command `vm list --short --backup`.


## `vm ping`

Shortcut to ping a VM with the static IP.

**Important**: this command only works if you have fixed an IP address on the VM.

## `vm ssh`

Shortcut to open a SSH session on the VM.

**Important**: this command only works if you have fixed an IP address on the VM.

Syntax:

    vm ssh [-h] name