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

    def __init__(self, domain, host_stats):
        self.domain = domain

        self.name = domain.name()
        self.host_stats = host_stats

        # CPU
        self.cpu_usage = 0
        self.cpu_time = 0

        # Memory
        self.host_mem = self.guest_mem = 0

        # Network
        self.net_rx_bytes = self.net_tx_bytes = 0
        self.net_rx_rate = self.net_tx_rate = 0

        # Storage
        self.block_rd_bytes = self.block_wr_bytes = 0
        self.block_rd_rate = self.block_wr_rate = 0

    @staticmethod
    def compute_cpu_usage(prev, cur, cpu_count):
        return min(
            (cur - prev) / (UPDATE_DATA_INTERVAL * cpu_count * 10**7),
            100
        )

    def update_cpu(self, stats):
        previous_cpu_time = self.cpu_time
        domain_cpu_count = stats.get('vcpu.current', 1)

        sum_time = 0
        for i in range(domain_cpu_count):
            sum_time += stats.get('vcpu.0.time', 0)
        current_cpu_time = sum_time / domain_cpu_count

        if previous_cpu_time > 0:
            self.cpu_usage = self.compute_cpu_usage(
                previous_cpu_time, current_cpu_time, self.host_stats.cpu_count
            )

        self.cpu_time = current_cpu_time

    def update_memory(self, stats):
        # Current memory allocated on the host
        self.host_mem = self.domain.memoryStats().get('rss', 0) * 1024

        # guest current max memory
        self.guest_mem = stats.get('balloon.maximum', 0) * 1024

    def update_network(self, stats):
        current_rx_bytes = stats.get('net.0.rx.bytes', 0)
        current_tx_bytes = stats.get('net.0.tx.bytes', 0)
        previous_rx_bytes = self.net_rx_bytes
        previous_tx_bytes = self.net_tx_bytes

        if previous_rx_bytes > 0:
            self.net_rx_rate = (
                (current_rx_bytes - previous_rx_bytes) * 8
                / UPDATE_DATA_INTERVAL
            )

        if previous_tx_bytes > 0:
            self.net_tx_rate = (
                (current_tx_bytes - previous_tx_bytes) * 8
                / UPDATE_DATA_INTERVAL
            )

        self.net_rx_bytes = current_rx_bytes
        self.net_tx_bytes = current_tx_bytes

    def update_storage(self, stats):
        current_rd_bytes = stats.get('block.0.rd.bytes', 0)
        current_wd_bytes = stats.get('block.0.wr.bytes', 0)
        previous_rd_bytes = self.block_rd_bytes
        previous_wd_bytes = self.block_wr_bytes

        if previous_rd_bytes > 0:
            self.block_rd_rate = (
                (current_rd_bytes - previous_rd_bytes) * 8
                / UPDATE_DATA_INTERVAL
            )

        if previous_wd_bytes > 0:
            self.block_wr_rate = (
                (current_wd_bytes - previous_wd_bytes) * 8
                / UPDATE_DATA_INTERVAL
            )

        self.block_rd_bytes = current_rd_bytes
        self.block_wr_bytes = current_wd_bytes

    def update(self, stats):
        for name in ('cpu', 'memory', 'network', 'storage'):
            getattr(self, 'update_%s' % name)(stats)

    def format(self, pattern):
        stats = {
            'name': self.name,
            'cpu_usage': round(self.cpu_usage),
            'guest_mem': si_unit(self.guest_mem, True) + 'B',
            'host_mem': si_unit(self.host_mem, True) + 'B',
            'net_rx': '{0}bps'.format(si_unit(self.net_rx_rate)),
            'net_tx': '{0}bps'.format(si_unit(self.net_tx_rate)),
            'block_rd': '{0}bps'.format(si_unit(self.block_rd_rate)),
            'block_wr': '{0}bps'.format(si_unit(self.block_wr_rate))
        }
        return pattern.format(**stats)


class HostStats:

    def __init__(self, connection):
        self._connection = connection

        host_info = connection.getInfo()
        self.cpu_count = host_info[2]

        self.mem_vms_total = 0
        self.mem_os = 0
        self.mem_total = 0
        self.mem_cached = 0

    def update(self, total_mem_domain):
        mem_stats = self._connection.getMemoryStats(
            libvirt.VIR_NODE_MEMORY_STATS_ALL_CELLS
        )

        self.mem_total = mem_stats['total'] * 1024
        self.mem_vms_total = total_mem_domain
        self.mem_os = ((mem_stats['total'] - mem_stats['free']
                       - mem_stats['cached']
                       - mem_stats['buffers']) * 1024
                       - total_mem_domain)
        self.mem_cached = (mem_stats['cached'] - mem_stats['buffers']) * 1024


class VMTop:

    def __init__(self):
        self._domains = {}

        self.libvirt_conn = Inventory.new_connection()

        self._sort_on = 'name'

        self.term_width = 0
        self.term_height = 0

        self.host_stats = HostStats(self.libvirt_conn)

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
                if event == ord('c'):
                    self._sort_on = 'cpu'
                elif event == ord('n'):
                    self._sort_on = 'name'
                elif event == ord('m'):
                    self._sort_on = 'mem'
                elif event == ord('q'):
                    break
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
        total_mem_domain = 0

        domains = self.libvirt_conn.getAllDomainStats(
            flags=libvirt.VIR_CONNECT_GET_ALL_DOMAINS_STATS_RUNNING
        )

        current_domains = set()
        for domain, libvirt_stats in domains:
            name = domain.name()
            current_domains.add(name)
            if name not in self._domains:
                self._domains[name] = DomainStats(domain, self.host_stats)

            self._domains[name].update(libvirt_stats)
            total_mem_domain += self._domains[name].host_mem

        # Delete all domains not active in domain stats list
        deleted_domains = set(self._domains.keys()) - current_domains
        list(map(self._domains.pop, deleted_domains))

        self.host_stats.update(total_mem_domain)

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
        if self.host_stats.mem_total > 0:
            ratio = self.host_stats.mem_os / self.host_stats.mem_total
            mem_os_size = round(ratio * (bar_graph_width - 2))
        self.screen.addstr(
            cur_line, posY,
            '|' * mem_os_size, self.RED_ON_BLACK
        )
        posY += mem_os_size

        mem_vms_size = 0
        if self.host_stats.mem_total > 0:
            ratio = self.host_stats.mem_vms_total / self.host_stats.mem_total
            mem_vms_size = round(ratio * (bar_graph_width - 2))
        self.screen.addstr(
            cur_line, posY,
            '|' * mem_vms_size, self.GREEN_ON_BLACK
        )
        posY += mem_vms_size

        mem_vms_size = 0
        if self.host_stats.mem_total > 0:
            ratio = self.host_stats.mem_cached / self.host_stats.mem_total
            mem_vms_size = round(ratio * (bar_graph_width - 2))
        self.screen.addstr(
            cur_line, posY,
            '|' * mem_vms_size, self.YELLOW_ON_BLACK
        )
        posY += mem_vms_size

        posY = bar_graph_width + bar_graph_offset + 2

        # Show memory takes by OS
        text = '{0}B'.format(si_unit(self.host_stats.mem_os, True))
        self.screen.addstr(cur_line, posY, text, self.RED_ON_BLACK)
        posY += len(text)

        text = ' / '
        self.screen.addstr(cur_line, posY, text)
        posY += len(text)

        # Show total memory used by vms
        text = '{0}B'.format(si_unit(self.host_stats.mem_vms_total, True))
        self.screen.addstr(cur_line, posY, text, self.GREEN_ON_BLACK)
        posY += len(text)

        # Show all physical memory on host
        self.screen.addstr(
            cur_line, posY,
            ' / {0}B'.format(si_unit(self.host_stats.mem_total, True)))

        cur_line += 2

        ###
        # TABLE HEADER
        ##
        TABLES_COLS = (
            '{name:15}', '{cpu_usage:>8}', '{guest_mem:>10}', '{host_mem:>10}',
            '{net_rx:>10}', '{net_tx:>10}',
            '{block_rd:>10}', '{block_wr:>10}'
        )

        COLS_NAME = dict(
            name='NAME', cpu_usage='%CPU', guest_mem='MEM',
            host_mem='HMEM', net_rx='NET RX', net_tx='NET TX',
            block_rd='BLK RD', block_wr='BLK WR')

        cur_line += 1
        self.screen.move(cur_line, 0)

        posY = 0

        if self._sort_on == 'cpu':
            sort_field = 1
        elif self._sort_on == 'mem':
            sort_field = 3
        else:
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
        domains = list(self._domains.values())
        domains.sort(key=lambda dom: dom.name)

        if self._sort_on == 'cpu':
            domains.sort(key=lambda dom: dom.cpu_usage, reverse=True)
        elif self._sort_on == 'mem':
            domains.sort(key=lambda dom: dom.host_mem, reverse=True)

        for domain in domains:
            if cur_line < self.term_height:
                self.screen.addstr(
                    cur_line, 0, domain.format(''.join(TABLES_COLS)))
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
