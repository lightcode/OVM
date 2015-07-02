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
restore       | Restore a VM
rm (remove)   | Remove a VM
save          | Save a VM
set           | Modify some properties of VM
ssh           | Shortcut to open a SSH session on the VM
start         | Start a VM
stop          | Halt a VM gracefully
storage       | Print the list of storage
templates     | Print the list of templates
top           | Show live stats about VMs



## `vm console`

Open a console on the VM.

To close the connection, you have to press `Ctrl+]` or `Ctrl+5`.

Syntax:

    vm console [-h] name

Read also [Configure a serial console on your VM](console.md).


## `vm create`

Create a new VM.

Syntax:

    vm create [-h] [--v] --template TEMPLATE --network NETWORK
              --storage STORAGE [--ip [IP]] [--size [SIZE]] [--vcpu [VCPU]]
              [--memory [MEMORY]]
              name


## `vm ping`

Shortcut to ping a VM with the static IP.

**Important**: this command only works if you have fixed an IP address on the VM.

    vm ping [-h] name


## `vm ssh`

Shortcut to open a SSH session on the VM.

**Important**: this command only works if you have fixed an IP address on the VM.

Syntax:

    vm ssh [-h] name
