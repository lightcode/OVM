Configure a serial console on your VM
=====================================

Debian
======

This tutorial is tested on Debian Wheezy.

You have to edit the file `/etc/inittab` :

    # Example how to put a getty on a serial line (for a terminal)
    #
    #T0:23:respawn:/sbin/getty -L ttyS0 9600 vt100
    #T1:23:respawn:/sbin/getty -L ttyS1 9600 vt100
    T0:23:respawn:/sbin/getty -8 -L 115200 ttyS0 xterm

I add a the last line in this file, it will add a TTY on the interface ttyS0, the serial port 0.

As you can see, I use the `xterm` terminal, you can install it on your system :

    # apt-get install xterm

It's more comfortable to resize the screen in applications like `less` or `vim`. To acheive that, you can use the command `reisize` from the xterm package. A serial interface don't send the heigth and the width like SSH. So you have to manualy resize the screen like this :

    $ resize

Of course, you can add the command above in you `.bashrc`.