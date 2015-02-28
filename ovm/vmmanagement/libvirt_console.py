#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
########################################################################
# Copyright 2014 Matthieu Gaignière                  http://lightcode.fr
########################################################################
# This file is part of OVM.
#
# OVM is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# OVM is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with OVM. If not, see <http://www.gnu.org/licenses/>.
########################################################################


import atexit
import libvirt
import os
import termios
import tty
from pyvirt.libvirtconn import LibvirtConn


class Console(object):
    def __init__(self, domain_name):
        libvirt.virEventRegisterDefaultImpl()
        libvirt.registerErrorHandler(self.error_handler, None)

        atexit.register(self.reset_term)
        self.attrs = termios.tcgetattr(0)
        tty.setraw(0)

        self.domain_name = domain_name
        self.connection = LibvirtConn.new_connection()
        self.domain = self.connection.lookupByName(domain_name)
        self.state = self.domain.state(0)
        self.connection.domainEventRegister(self.lifecycle_callback, self)
        self.stream = None
        self.run_console = True

    def error_handler(self, unused, error):
        # The console stream errors on VM shutdown; we don't care
        if (error[0] == libvirt.VIR_ERR_RPC and
                error[1] == libvirt.VIR_FROM_STREAMS):
            return

    def reset_term(self):
        termios.tcsetattr(0, termios.TCSADRAIN, self.attrs)

    def start(self):
        self.stdin_watch = libvirt.virEventAddHandle(
            0, libvirt.VIR_EVENT_HANDLE_READABLE, self.stdin_callback, self)

        print("Escape character is ^]")

        while self.check_console():
            libvirt.virEventRunDefaultImpl()

    def check_console(self):
        if (self.state[0] == libvirt.VIR_DOMAIN_RUNNING or
           self.state[0] == libvirt.VIR_DOMAIN_PAUSED):
            if self.stream is None:
                self.stream = self.connection.newStream(
                    libvirt.VIR_STREAM_NONBLOCK)
                self.domain.openConsole(None, self.stream, 0)
                self.stream.eventAddCallback(
                    libvirt.VIR_STREAM_EVENT_READABLE, self.stream_callback,
                    self)
        elif self.stream:
            self.stream.eventRemoveCallback()
            self.stream = None

        return self.run_console

    def lifecycle_callback(self, connection, domain, event, detail, _):
        self.state = self.domain.state(0)

    def stream_callback(self, stream, events, _):
        try:
            received_data = self.stream.recv(1024)
        except:
            return
        os.write(0, received_data)

    def stdin_callback(self, watch, fd, events, _):
        readbuf = os.read(fd, 1024)
        # Close connection when we recieve a ^[
        if readbuf == b'\x1d':
            self.run_console = False
            return
        if self.stream:
            self.stream.send(readbuf)

    @classmethod
    def open_console(cls, domain_name):
        console = Console(domain_name)
        console.start()
