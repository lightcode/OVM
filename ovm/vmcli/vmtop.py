#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
import libvirt
import threading
import time

from ovm.lvconnect import LibvirtConnect
from ovm.utils.printer import si_unit


UPDATE_DATA_INTERVAL = 1
REFRESH_INTERVAL = 0.5

SORT_NAME, SORT_CPU, SORT_MEM = 0, 1, 3


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
        return min((cur - prev) / (UPDATE_DATA_INTERVAL * cpu_count * 10**7), 100)

    def update_cpu(self, stats):
        previous_cpu_time = self.cpu_time
        domain_cpu_count = stats.get("vcpu.current", 1)

        sum_time = 0
        for i in range(domain_cpu_count):
            sum_time += stats.get("vcpu.0.time", 0)
        current_cpu_time = sum_time / domain_cpu_count

        if previous_cpu_time > 0:
            self.cpu_usage = self.compute_cpu_usage(
                previous_cpu_time, current_cpu_time, self.host_stats.cpu_count
            )

        self.cpu_time = current_cpu_time

    def update_memory(self, stats):
        # Current memory allocated on the host
        self.host_mem = self.domain.memoryStats().get("rss", 0) * 1024

        # guest current max memory
        self.guest_mem = stats.get("balloon.maximum", 0) * 1024

    def update_network(self, stats):
        current_rx_bytes = stats.get("net.0.rx.bytes", 0)
        current_tx_bytes = stats.get("net.0.tx.bytes", 0)
        previous_rx_bytes = self.net_rx_bytes
        previous_tx_bytes = self.net_tx_bytes

        if previous_rx_bytes > 0:
            self.net_rx_rate = (
                (current_rx_bytes - previous_rx_bytes) * 8 / UPDATE_DATA_INTERVAL
            )

        if previous_tx_bytes > 0:
            self.net_tx_rate = (
                (current_tx_bytes - previous_tx_bytes) * 8 / UPDATE_DATA_INTERVAL
            )

        self.net_rx_bytes = current_rx_bytes
        self.net_tx_bytes = current_tx_bytes

    def update_storage(self, stats):
        current_rd_bytes = stats.get("block.0.rd.bytes", 0)
        current_wd_bytes = stats.get("block.0.wr.bytes", 0)
        previous_rd_bytes = self.block_rd_bytes
        previous_wd_bytes = self.block_wr_bytes

        if previous_rd_bytes > 0:
            self.block_rd_rate = (
                (current_rd_bytes - previous_rd_bytes) * 8 / UPDATE_DATA_INTERVAL
            )

        if previous_wd_bytes > 0:
            self.block_wr_rate = (
                (current_wd_bytes - previous_wd_bytes) * 8 / UPDATE_DATA_INTERVAL
            )

        self.block_rd_bytes = current_rd_bytes
        self.block_wr_bytes = current_wd_bytes

    def update(self, stats):
        for name in ("cpu", "memory", "network", "storage"):
            getattr(self, "update_%s" % name)(stats)

    def format(self, pattern):
        stats = {
            "name": self.name,
            "cpu_usage": round(self.cpu_usage),
            "guest_mem": si_unit(self.guest_mem, True) + "B",
            "host_mem": si_unit(self.host_mem, True) + "B",
            "net_rx": "{0}bps".format(si_unit(self.net_rx_rate)),
            "net_tx": "{0}bps".format(si_unit(self.net_tx_rate)),
            "block_rd": "{0}bps".format(si_unit(self.block_rd_rate)),
            "block_wr": "{0}bps".format(si_unit(self.block_wr_rate)),
        }
        return pattern.format(**stats)


class HostStats:
    def __init__(self, connection):
        self._connection = connection

        self.hostname = connection.getHostname()

        host_info = connection.getInfo()
        self.cpu_count = host_info[2]
        self.cpu_freq = host_info[3] * (10**6)
        self.cpu_time = 0
        self.cpu_usage = 0

        self.mem_vms_total = 0
        self.mem_os = 0
        self.mem_total = 0
        self.mem_cached = 0

        self.domain_count = 0

    def update(self, total_mem_domain, domain_count):
        self.domain_count = domain_count

        host_info = self._connection.getInfo()
        self.cpu_freq = host_info[3] * (10**6)

        cpu_stats = self._connection.getCPUStats(libvirt.VIR_NODE_CPU_STATS_ALL_CPUS)

        cpu_time = (
            sum((cpu_stats[k] for k in ("kernel", "user", "iowait"))) / self.cpu_count
        )

        if self.cpu_time > 0:
            self.cpu_usage = min(
                1, ((cpu_time - self.cpu_time) / (UPDATE_DATA_INTERVAL * 10**9))
            )
        self.cpu_time = cpu_time

        mem_stats = self._connection.getMemoryStats(
            libvirt.VIR_NODE_MEMORY_STATS_ALL_CELLS
        )

        self.mem_total = mem_stats["total"] * 1024
        self.mem_vms_total = total_mem_domain
        self.mem_os = (
            mem_stats["total"]
            - mem_stats["free"]
            - mem_stats["cached"]
            - mem_stats["buffers"]
        ) * 1024 - total_mem_domain
        self.mem_cached = (mem_stats["cached"] - mem_stats["buffers"]) * 1024


class VMTop:
    def __init__(self):
        self._domains = {}

        self.libvirt_conn = LibvirtConnect.get_connection()

        self._sort_on = SORT_NAME

        self.host_stats = HostStats(self.libvirt_conn)

        self.screen = curses.initscr()
        self.init_terminal()

        # Init colors
        colors = (
            ("TABLE_HEADER", curses.COLOR_BLACK, curses.COLOR_GREEN),
            ("TABLE_HEADER_SELECTED", curses.COLOR_BLACK, curses.COLOR_CYAN),
            ("RED_ON_BLACK", curses.COLOR_RED, curses.COLOR_BLACK),
            ("GREEN_ON_BLACK", curses.COLOR_GREEN, curses.COLOR_BLACK),
            ("CYAN_ON_BLACK", curses.COLOR_CYAN, curses.COLOR_BLACK),
            ("BLACK_ON_CYAN", curses.COLOR_BLACK, curses.COLOR_CYAN),
            ("YELLOW_ON_BLACK", curses.COLOR_YELLOW, curses.COLOR_BLACK),
        )

        for i, color in enumerate(colors, 1):
            name, fg, bg = color
            curses.init_pair(i, fg, bg)
            setattr(self, name, curses.color_pair(i))

        try:
            self.main()
        finally:
            self.reset_terminal()

    def main(self):
        refresh_thread = threading.Thread(target=self.refresh)
        refresh_thread.daemon = True
        refresh_thread.start()

        update_data_thread = threading.Thread(target=self.update_data)
        update_data_thread.daemon = True
        update_data_thread.start()

        while True:
            event = self.screen.getch()
            if event == ord("c"):
                self._sort_on = SORT_CPU
            elif event == ord("n"):
                self._sort_on = SORT_NAME
            elif event == ord("m"):
                self._sort_on = SORT_MEM
            elif event == ord("q"):
                break

    def init_terminal(self):
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.screen.keypad(1)
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

        domain_count = len(current_domains)

        self.host_stats.update(total_mem_domain, domain_count)

    def draw_host_bar(self, line):
        style = self.CYAN_ON_BLACK

        bar_format = "  ::  ".join(
            (
                "{hostname}",
                "CPU: {cpu_count} ({cpu_freq} MHz)",
                "Memory: {mem_total}iB",
                "Domains: {domain_count}",
            )
        )

        text = bar_format.format(
            hostname=self.host_stats.hostname,
            cpu_count=self.host_stats.cpu_count,
            cpu_freq=int(self.host_stats.cpu_freq / 10**6),
            mem_total=si_unit(self.host_stats.mem_total),
            domain_count=self.host_stats.domain_count,
        )

        self.screen.addstr(line, 0, text, style)
        self.screen.clrtoeol()

    def draw_cpu_bar(self, line):
        # Some params
        bar_graph_width = 40

        # Inialize the line
        self.screen.move(line, 0)
        self.screen.clrtoeol()

        # Show 'CPU'
        self.screen.move(line, 1)
        self.screen.addstr("CPU", self.CYAN_ON_BLACK)

        # Print the left side of the bar graph
        self.screen.addstr("  [")

        # Print the memory take by OS
        pipe_count = int(round(self.host_stats.cpu_usage * bar_graph_width))
        self.screen.addstr("|" * pipe_count, self.RED_ON_BLACK)

        # Print the right side of the bar graph
        _, x = self.screen.getyx()
        self.screen.move(line, x + bar_graph_width - pipe_count)
        self.screen.addstr("]  ")

        self.screen.addstr("{0} %".format(round(self.host_stats.cpu_usage * 100)))

    def draw_memory_bar(self, line):
        current_bar_size = 0

        # Some params
        bar_graph_width = 40

        # Inialize the line
        self.screen.move(line, 0)
        self.screen.clrtoeol()

        # Show 'Mem'
        self.screen.move(line, 1)
        self.screen.addstr("Mem", self.CYAN_ON_BLACK)

        # Print the left side of the bar graph
        self.screen.addstr("  [")

        # Print the memory take by OS
        if self.host_stats.mem_total > 0:
            ratio = self.host_stats.mem_os / self.host_stats.mem_total
            mem_os_size = int(round(ratio * bar_graph_width))
            self.screen.addstr("|" * mem_os_size, self.RED_ON_BLACK)
            current_bar_size += mem_os_size

        # Print the memory take by VMs
        if self.host_stats.mem_total > 0:
            ratio = self.host_stats.mem_vms_total / self.host_stats.mem_total
            mem_vms_size = int(round(ratio * bar_graph_width))
            self.screen.addstr("|" * mem_vms_size, self.GREEN_ON_BLACK)
            current_bar_size += mem_vms_size

        # Print the memory cached
        if self.host_stats.mem_total > 0:
            ratio = self.host_stats.mem_cached / self.host_stats.mem_total
            mem_cached_size = int(round(ratio * bar_graph_width))
            self.screen.addstr("|" * mem_cached_size, self.YELLOW_ON_BLACK)
            current_bar_size += mem_cached_size

        # Print the right side of the bar graph
        _, x = self.screen.getyx()
        self.screen.move(line, x + bar_graph_width - current_bar_size)
        self.screen.addstr("]  ")

        # Print the text aside
        self.screen.addstr(
            "{0}B".format(si_unit(self.host_stats.mem_os, True)), self.RED_ON_BLACK
        )

        self.screen.addstr(" / ")

        self.screen.addstr(
            "{0}B".format(si_unit(self.host_stats.mem_vms_total, True)),
            self.GREEN_ON_BLACK,
        )

        self.screen.addstr(" / {0}B".format(si_unit(self.host_stats.mem_total, True)))

    def draw_domains(self, line):
        # Initialize columns
        TABLES_COLS = (
            "{name:15}",
            "{cpu_usage:>8}",
            "{guest_mem:>10}",
            "{host_mem:>10}",
            "{net_rx:>10}",
            "{net_tx:>10}",
            "{block_rd:>10}",
            "{block_wr:>10}",
        )

        # Prepare table header
        COLS_NAME = dict(
            name="NAME",
            cpu_usage="%CPU",
            guest_mem="MEM",
            host_mem="HOST MEM",
            net_rx="NET RX",
            net_tx="NET TX",
            block_rd="BLK RD",
            block_wr="BLK WR",
        )

        # Draw the header
        self.screen.move(line, 0)

        for i, pattern in enumerate(TABLES_COLS):
            if self._sort_on == i:
                color = self.TABLE_HEADER_SELECTED
            else:
                color = self.TABLE_HEADER
            text = pattern.format(**COLS_NAME)
            self.screen.addstr(text, color)

        self.screen.addstr(
            " " * (self.screen.getmaxyx()[1] - self.screen.getyx()[1]),
            self.TABLE_HEADER,
        )

        domains = list(self._domains.values())
        domains.sort(key=lambda dom: dom.name)

        if self._sort_on == SORT_CPU:
            domains.sort(key=lambda dom: dom.cpu_usage, reverse=True)
        elif self._sort_on == SORT_MEM:
            domains.sort(key=lambda dom: dom.host_mem, reverse=True)

        for domain in domains:
            self.screen.addstr(domain.format("".join(TABLES_COLS)))
            self.screen.clrtoeol()
            self.screen.addch("\n")
        self.screen.clrtobot()

    def refresh_interface(self):
        self.draw_host_bar(0)
        self.draw_cpu_bar(2)
        self.draw_memory_bar(3)
        self.draw_domains(5)
        self.screen.refresh()

    def refresh(self):
        while True:
            try:
                self.refresh_interface()
            except curses.error:
                pass
            finally:
                time.sleep(REFRESH_INTERVAL)


if __name__ == "__main__":
    VMTop()
