#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
########################################################################
# Copyright 2015 Matthieu Gaignière                  http://lightcode.fr
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


import curses
import fcntl
import libvirt
import struct
import termios
import threading
import time

from ovm.inventory import Inventory
from ovm.utils.printer import si_unit


UPDATE_DATA_INTERVAL = 1
REFRESH_INTERVAL = 0.5


class DomainStats:

    def __init__(self, domain, stats):
        self.domain = domain
        self.stats = stats


class Stats:
    def __init__(self):
        self.vms = {}
        self.mem_vms_total = 0
        self.mem_os = 0
        self.mem_total = 0
        self.mem_cached = 0


class VMTop:
    def __init__(self):
        self.libvirt_conn = Inventory.new_connection()

        self._sort_on = 'cpu_usage'

        self.term_width = 0
        self.term_height = 0

        self.stats = Stats()

        self.screen = curses.initscr()
        self.init_terminal()

        # Init colors
        colors = (
            ('BLACK_ON_GREEN', curses.COLOR_BLACK, curses.COLOR_GREEN),
            ('RED_ON_BLACK', curses.COLOR_RED, curses.COLOR_BLACK),
            ('GREEN_ON_BLACK', curses.COLOR_GREEN, curses.COLOR_BLACK),
            ('CYAN_ON_BLACK',  6, curses.COLOR_BLACK),
            ('BLACK_ON_CYAN',  curses.COLOR_BLACK, 6),
            ('YELLOW_ON_BLACK', curses.COLOR_YELLOW, curses.COLOR_BLACK)
        )

        for i, color in enumerate(colors, 1):
            name, fg, bg = color
            curses.init_pair(i, fg, bg)
            setattr(self, name, curses.color_pair(i))

        refresh_thread = threading.Thread(target=self.refresh)
        refresh_thread.daemon = True
        refresh_thread.start()

        update_data_thread = threading.Thread(target=self.update_data)
        update_data_thread.daemon = True
        update_data_thread.start()

        try:
            while True:
                event = self.screen.getch()
                if event == ord('q'):
                    break
                if event == ord('c'):
                    self._sort_on = 'cpu_usage'
                if event == ord('n'):
                    self._sort_on = 'name'
                if event == ord('m'):
                    self._sort_on = 'rss_float'
                elif event == curses.KEY_RESIZE:
                    self.resize()
        finally:
            self.reset_terminal()

    def init_terminal(self):
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.screen.keypad(1)
        self.resize()
        self.screen.clear()
        self.screen.refresh()

    def reset_terminal(self):
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()

    def update_data(self):
        while True:
            self._update_data()
            time.sleep(UPDATE_DATA_INTERVAL)

    def _update_data(self):
        all_stats = {}
        total_mem_domain = 0
        host_info = self.libvirt_conn.getInfo()
        cpu_count = host_info[2]

        domains = self.libvirt_conn.getAllDomainStats(
            flags=libvirt.VIR_CONNECT_GET_ALL_DOMAINS_STATS_RUNNING
        )

        for domain, libvirt_stats in domains:

            name = domain.name()
            # Current memory allocated on the host
            rss = domain.memoryStats().get('rss', 0) * 1024

            old_stats = self.stats.vms.get(name)

            # guest current max memory
            guest_mem = libvirt_stats.get('balloon.maximum', 0) * 1024

            cpu = cur_cpu_time = 0
            net0_tx = net0_rx = net0_rx_cur = net0_tx_cur = 0
            if old_stats is not None:
                cpu_prev_time = old_stats.stats.get('cputime', 0)
                cur_cpu_time = int(libvirt_stats.get('vcpu.0.time', 0))
                if cpu_prev_time > 0:
                    cpu = (cur_cpu_time - cpu_prev_time) \
                        / (UPDATE_DATA_INTERVAL * cpu_count * 10**7)
                    cpu = min(cpu, 100)

                net0_rx_prev = old_stats.stats.get('net0_rx_bytes', 0)
                net0_rx_cur = libvirt_stats.get('net.0.rx.bytes', 0)
                if net0_rx_prev > 0:
                    net0_rx = ((net0_rx_cur - net0_rx_prev)
                               / UPDATE_DATA_INTERVAL)

                net0_tx_prev = old_stats.stats.get('net0_tx_bytes', 0)
                net0_tx_cur = libvirt_stats.get('net.0.tx.bytes', 0)
                if net0_tx_prev > 0:
                    net0_tx = ((net0_tx_cur - net0_tx_prev)
                               / UPDATE_DATA_INTERVAL)

            stats = {
                'name': name,
                'cputime': cur_cpu_time,
                'cpu_usage': round(cpu),
                'mem': si_unit(guest_mem, True) + 'B',
                'rss': si_unit(rss, True) + 'B',
                'rss_float': rss,
                'net0_rx_bytes': net0_rx_cur,
                'net0_tx_bytes': net0_tx_cur,
                'net0_rx': '{0}Bps'.format(si_unit(net0_rx * 8)),
                'net0_tx': '{0}Bps'.format(si_unit(net0_tx * 8))
            }
            total_mem_domain += stats['rss_float']

            all_stats[name] = DomainStats(domain, stats)

        self.stats.vms = all_stats

        mem_stats = self.libvirt_conn.getMemoryStats(
            libvirt.VIR_NODE_MEMORY_STATS_ALL_CELLS
        )

        self.stats.mem_total = mem_stats['total'] * 1024
        self.stats.mem_vms_total = total_mem_domain
        self.stats.mem_os = ((mem_stats['total'] - mem_stats['free']
                              - mem_stats['cached']
                              - mem_stats['buffers']) * 1024
                             - total_mem_domain)
        self.stats.mem_cached = (mem_stats['cached']
                                 - mem_stats['buffers']) * 1024

    def resize(self):
        w, h = VMTop.terminal_size()
        self.term_width = w
        self.term_height = h
        curses.resizeterm(h, w)

    def refresh_interface(self):
        cur_line = 1

        ###
        # MEMORY LINE
        ##

        # Clean the whole line
        self.screen.move(cur_line, 0)
        self.screen.clrtoeol()

        # Show 'Mem'
        self.screen.addstr(cur_line, 1, 'Mem', self.CYAN_ON_BLACK)
        bar_graph_offset = 6
        bar_graph_width = 40
        self.screen.addstr(cur_line, bar_graph_offset, '[')
        self.screen.addstr(cur_line, bar_graph_offset + bar_graph_width, ']')

        posY = bar_graph_offset + 1

        mem_os_size = 0
        if self.stats.mem_total > 0:
            ratio = self.stats.mem_os / self.stats.mem_total
            mem_os_size = round(ratio * (bar_graph_width - 2))
        self.screen.addstr(
            cur_line, posY,
            '|' * mem_os_size, self.RED_ON_BLACK
        )
        posY += mem_os_size

        mem_vms_size = 0
        if self.stats.mem_total > 0:
            ratio = self.stats.mem_vms_total / self.stats.mem_total
            mem_vms_size = round(ratio * (bar_graph_width - 2))
        self.screen.addstr(
            cur_line, posY,
            '|' * mem_vms_size, self.GREEN_ON_BLACK
        )
        posY += mem_vms_size

        mem_vms_size = 0
        if self.stats.mem_total > 0:
            ratio = self.stats.mem_cached / self.stats.mem_total
            mem_vms_size = round(ratio * (bar_graph_width - 2))
        self.screen.addstr(
            cur_line, posY,
            '|' * mem_vms_size, self.YELLOW_ON_BLACK
        )
        posY += mem_vms_size

        posY = bar_graph_width + bar_graph_offset + 2

        # Show memory takes by OS
        text = '{0}B'.format(si_unit(self.stats.mem_os, True))
        self.screen.addstr(cur_line, posY, text, self.RED_ON_BLACK)
        posY += len(text)

        text = ' / '
        self.screen.addstr(cur_line, posY, text)
        posY += len(text)

        # Show total memory used by vms
        text = '{0}B'.format(si_unit(self.stats.mem_vms_total, True))
        self.screen.addstr(cur_line, posY, text, self.GREEN_ON_BLACK)
        posY += len(text)

        # Show all physical memory on host
        self.screen.addstr(
            cur_line, posY,
            ' / {0}B'.format(si_unit(self.stats.mem_total, True)))

        cur_line += 2

        ###
        # TABLE HEADER
        ##
        TABLES_COLS = (
            '{name:15}', '{cpu_usage:>10}', '{mem:>10}', '{rss:>10}',
            '{net0_rx:>10}', '{net0_tx:>10}'
        )

        COLS_NAME = dict(
            name='NAME', cpu_usage='%CPU', mem='MEM',
            rss='HMEM', net0_rx='NET RX', net0_tx='NET TX')

        cur_line += 1
        self.screen.move(cur_line, 0)

        posY = 0

        if self._sort_on == 'cpu_usage':
            sort_field = 1
        elif self._sort_on == 'rss_float':
            sort_field = 2
        elif self._sort_on == 'name':
            sort_field = 0

        for i, pattern in enumerate(TABLES_COLS):
            if sort_field == i:
                color = self.BLACK_ON_CYAN
            else:
                color = self.BLACK_ON_GREEN
            text = pattern.format(**COLS_NAME)
            self.screen.addstr(cur_line, posY, text, color)
            posY += len(text)

        self.screen.addstr(
            cur_line, posY, ' '*(self.term_width - posY), self.BLACK_ON_GREEN)

        cur_line += 1
        self.screen.clrtoeol()

        ###
        # PRINT ALL VMS
        ###
        vms = list(self.stats.vms.values())
        if self._sort_on == 'name':
            reverse = False
        else:
            reverse = True

        vms.sort(key=lambda v: v.stats.get('name'))
        vms.sort(key=lambda v: v.stats.get(self._sort_on, 0), reverse=reverse)
        for vm in vms:
            if cur_line < self.term_height:
                text = ''.join(TABLES_COLS).format(**vm.stats)
                self.screen.addstr(cur_line, 0, text)
                self.screen.clrtoeol()
            cur_line += 1

        ###
        # CLEAR AND REFRESH
        ###
        self.screen.clrtobot()
        self.screen.refresh()

    def refresh(self):
        while True:
            try:
                self.refresh_interface()
            except curses.error:
                pass
            finally:
                time.sleep(REFRESH_INTERVAL)

    @classmethod
    def terminal_size(cls):
        h, w, hp, wp = struct.unpack('HHHH', fcntl.ioctl(
            0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)
        ))
        return w, h


if __name__ == '__main__':
    VMTop()
