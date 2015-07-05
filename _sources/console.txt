.. _configure-serial:

Configure a serial console on your VM
=====================================

CentOS
------

CentOS 6
~~~~~~~~

Firstly, we need to install ``xterm``:

.. code-block:: console

    # yum install xterm

The first step is to add the file ``/etc/init/ttyS0.conf``. You can
directly enter this command:

.. code-block:: bash

    cat <<EOF > /etc/init/ttyS0.conf
    start on runlevel [345]
    stop on runlevel [S016]

    respawn
    instance /dev/ttyS0
    exec /sbin/agetty -8 -L 115200 ttyS0 xterm
    EOF

You need to activate the authentication on the ttyS0:

.. code-block:: console

    # echo ttyS0 > /etc/securetty



CentOS 7
~~~~~~~~

Firstly, we need to install ``xterm``:

.. code-block:: console

    # yum install xterm

You can run the following script to enable a TTY on ttyS0:


.. code-block:: bash

    cp "/usr/lib/systemd/system/serial-getty@.service" "/etc/systemd/system/serial-getty@ttyS0.service"
    sed -i 's|115200,38400,9600|115200,38400,9600 xterm|g' "/etc/systemd/system/serial-getty@ttyS0.service"
    ln -s "/etc/systemd/system/serial-getty@ttyS0.service" /etc/systemd/system/getty.target.wants
    systemctl daemon-reload
    systemctl start "serial-getty@ttyS0.service"



Debian
------

Debian 7
~~~~~~~~

Firstly, we need to install ``xterm``:

.. code-block:: console

    # apt-get install xterm

You have to edit the file ``/etc/inittab`` :

::

    # Example how to put a getty on a serial line (for a terminal)
    #
    #T0:23:respawn:/sbin/getty -L ttyS0 9600 vt100
    #T1:23:respawn:/sbin/getty -L ttyS1 9600 vt100
    T0:23:respawn:/sbin/getty -8 -L 115200 ttyS0 xterm

I add the line after the serial line documentation. It will add a TTY on
the interface ttyS0, the serial port 0.



Debian 8
~~~~~~~~

Firstly, we need to install ``xterm``:

.. code-block:: console

    # apt-get install xterm

You can run the following script to enable a TTY on ttyS0:

.. code-block:: bash

    cp "/lib/systemd/system/serial-getty@.service" "/etc/systemd/system/serial-getty@ttyS0.service"
    sed -i 's|$TERM|xterm|g' "/etc/systemd/system/serial-getty@ttyS0.service"
    ln -s "/etc/systemd/system/serial-getty@ttyS0.service" /etc/systemd/system/getty.target.wants
    systemctl daemon-reload
    systemctl start "serial-getty@ttyS0.service"



Bonus: resize automatically the terminal
----------------------------------------

It’s more comfortable to resize the screen in applications like ``less``
or ``vim``. To achieve that, you can use the command ``resize`` from the
xterm package. A serial interface don’t send the height and the width of
the window like SSH. You can execute this command at the session
startup:

.. code-block:: bash

    cat <<EOF > /etc/profile.d/resize-console.sh
    if [ "\$(tty)" == "/dev/ttyS0" ]; then
      resize &> /dev/null
    fi
    EOF
