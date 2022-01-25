#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import atexit
import libvirt
import os
import sys
import termios
import tty

from ovm.lvconnect import LibvirtConnect


def error_handler(_, error):
    # The console stream errors on VM shutdown; we don't care
    if error[0] == libvirt.VIR_ERR_RPC and error[1] == libvirt.VIR_FROM_STREAMS:
        return


class Console:
    def __init__(self, domain_name):
        self.domain_name = domain_name
        self.stream = None
        self.run_console = True

    def reset_term(self):
        termios.tcsetattr(0, termios.TCSADRAIN, self.attrs)

    def start(self):
        libvirt.virEventRegisterDefaultImpl()
        libvirt.registerErrorHandler(error_handler, None)

        atexit.register(self.reset_term)
        self.attrs = termios.tcgetattr(0)
        tty.setraw(0)

        self.connection = LibvirtConnect.get_connection()
        self.domain = self.connection.lookupByName(self.domain_name)
        self.state = self.domain.state(0)
        self.connection.domainEventRegister(self.lifecycle_callback, self)

        sys.stdout.write("Press Control+] to quit.\n\r")
        sys.stdout.flush()

        libvirt.virEventAddHandle(
            0, libvirt.VIR_EVENT_HANDLE_READABLE, self.stdin_callback, None
        )

        while self.check_console():
            libvirt.virEventRunDefaultImpl()

        sys.stdout.write("\n\rExited.\n\r")
        sys.stdout.flush()

    def check_console(self):
        if self.state[0] != libvirt.VIR_DOMAIN_RUNNING:
            self.stream.finish()
            return False

        if self.stream is None:
            self.stream = self.connection.newStream(libvirt.VIR_STREAM_NONBLOCK)
            self.domain.openConsole(None, self.stream)
            self.stream.eventAddCallback(
                libvirt.VIR_STREAM_EVENT_READABLE, self.stream_callback, None
            )

        return self.run_console

    def lifecycle_callback(self, connection, domain, event, detail, _):
        self.state = domain.state(0)

    def stream_callback(self, stream, events, _):
        try:
            received_data = stream.recv(1024)
        except:
            return
        os.write(0, received_data)

    def stdin_callback(self, watch, fd, events, _):
        readbuf = os.read(fd, 1024)
        # Close connection when we receive a ^]
        if readbuf == b"\x1d":
            self.run_console = False
            return
        if self.stream:
            self.stream.send(readbuf)

    @staticmethod
    def open_console(domain_name):
        console = Console(domain_name)
        console.start()
