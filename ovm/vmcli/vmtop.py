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


class DomainStats:

    def __init__(self, domain, stats):
        self.domain = domain
        self.stats = stats


class Stats:
    def __init__(self):
        self.vms = {}
        self.mem_vms_total = 0
        self.mem_free = 0
        self.mem_os = 0
        self.mem_total = 0


class VMTop:
    def __init__(self):
        self.libvirt_conn = Inventory.new_connection()

        self.sort_param = 'cpu'
        self.term_width = 0
        self.term_height = 0

        self.stats = Stats()

        self.screen = curses.initscr()
        self.init_terminal()

        # Black on green
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
        # Grey on black
        curses.init_pair(2, 8, curses.COLOR_BLACK)
        # Red on black
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        # Green on black
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        # Dark cyan on black
        curses.init_pair(5, 6, curses.COLOR_BLACK)

        clock = threading.Thread(target=self.update)
        clock.daemon = True
        clock.start()

        update_data = threading.Thread(target=self.update_data)
        update_data.daemon = True
        update_data.start()

        try:
            while True:
                event = self.screen.getch()
                if event == ord('q'):
                    break
                # elif event == ord('c'):
                #     self.sort_param = 'cpu'
                # elif event == ord('r'):
                #     self.sort_param = 'rss'
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

        for domain, libvirt_stats in self.libvirt_conn.getAllDomainStats(
                flags=libvirt.VIR_CONNECT_GET_ALL_DOMAINS_STATS_RUNNING
                ):

            name = domain.name()
            # Current memory allocated on the host
            rss = domain.memoryStats().get('rss', 0) * 1024

            old_stats = self.stats.vms.get(name)

            # guest current max memory
            guest_mem = libvirt_stats.get('balloon.maximum', 0) * 1024

            cpu = 0
            cur_cpu_time = 0

            if old_stats is not None:
                cpu_prev_time = old_stats.stats.get('cputime', 0)
                cur_cpu_time = int(libvirt_stats.get('vcpu.0.time', 0))
                if cpu_prev_time > 0:
                    cpu = (cur_cpu_time - cpu_prev_time) \
                        / (UPDATE_DATA_INTERVAL * cpu_count * 10**7)
                    cpu = min(cpu, 100)

            stats = {
                'name': domain.name(),
                'cputime': cur_cpu_time,
                'cpu_usage': cpu,
                'mem': si_unit(guest_mem, True) + 'B',
                'rss': si_unit(rss, True) + 'B',
                'rss_float': rss
            }
            total_mem_domain += stats['rss_float']

            all_stats[name] = DomainStats(domain, stats)

        self.stats.vms = all_stats

        self.stats.mem_free = self.libvirt_conn.getFreeMemory()
        self.stats.mem_total = host_info[1] * (1024**2)
        self.stats.mem_vms_total = total_mem_domain

        '''
        self.stats.vms.update(vms)
        self.stats.mem_vms_total = mem_vms_total
        self.stats.mem_free = mem_free
        self.stats.mem_os = mem_total - mem_free - mem_vms_total
        self.stats.mem_total = mem_total
        '''

    def resize(self):
        w, h = VMTop.terminal_size()
        self.term_width = w
        self.term_height = h
        curses.resizeterm(h, w)

    def print_line(self, text, style=curses.A_NORMAL):
        self.screen.addstr(text.ljust(self.term_width - 1), style)

    def _sort_by_cpu(self, value):
        return value.get('cpu', 0)

    def _sort_by_rss(self, value):
        return value.get('rss_float', 0)

    def refresh_interface(self):
        cur_line = 1

        # Bar graph
        self.screen.addstr(cur_line, 1, 'Mem', curses.color_pair(5))
        bar_graph_offset = 6
        bar_graph_width = 40
        self.screen.addstr(cur_line, bar_graph_offset, '[')
        self.screen.addstr(cur_line, bar_graph_offset + bar_graph_width, ']')

        mem_os_size = 0
        if self.stats.mem_total > 0:
            ratio = self.stats.mem_os / self.stats.mem_total
            mem_os_size = round(ratio * (bar_graph_width - 2))
        self.screen.addstr(
            cur_line, bar_graph_offset + 1,
            '|' * mem_os_size, curses.color_pair(3)
        )

        mem_vms_size = 0
        if self.stats.mem_total > 0:
            ratio = self.stats.mem_vms_total / self.stats.mem_total
            mem_vms_size = round(ratio * (bar_graph_width - 2))
        self.screen.addstr(
            cur_line, bar_graph_offset + mem_os_size + 1,
            '|' * mem_vms_size, curses.color_pair(4)
        )

        # Erase all old characters on bar graph
        self.screen.addstr(
            cur_line,
            bar_graph_offset + mem_os_size + mem_vms_size + 1,
            ' ' * (bar_graph_width - 2 - mem_os_size - mem_vms_size))

        bar = '{0}B / {1}B'.format(
            si_unit(self.stats.mem_vms_total, True),
            si_unit(self.stats.mem_total, True)
        )
        self.screen.addstr(
            cur_line, bar_graph_width + bar_graph_offset + 2, bar
        )

        cur_line += 2

        # Table header
        cur_line += 1
        self.screen.move(cur_line, 0)
        pattern = '{name:15} {cpu_usage:>8} {mem:>8} {rss:>8}'
        self.print_line(pattern.format(
            name='NAME', cpu_usage='%CPU', mem='MEM', rss='HMEM'
        ), curses.color_pair(1))
        cur_line += 1

        pattern = '{name:15} {cpu_usage:>8.1f} {mem:>8} {rss:>8}'
        for vm in self.stats.vms.values():
            stats = vm.stats
            style = 0
            if cur_line < self.term_width:
                self.screen.move(cur_line, 0)
                self.print_line(pattern.format(**stats), style)
            cur_line += 1

        self.screen.refresh()

    def update(self):
        while True:
            try:
                self.refresh_interface()
            except curses.error:
                pass
            finally:
                time.sleep(0.2)

    @classmethod
    def terminal_size(cls):
        h, w, hp, wp = struct.unpack('HHHH', fcntl.ioctl(
            0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)
        ))
        return w, h


if __name__ == '__main__':
    VMTop()
