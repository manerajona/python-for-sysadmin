#!/usr/bin/env python3
"""
system_monitor.py

A small, continuously-running system monitor that prints OS, memory, disk and
top CPU-consuming processes to stdout in a tabular format.

Usage:
    python system_monitor.py
    (press Ctrl-C to exit)
"""

import os
import platform
import socket
import time

import psutil
from prettytable import PrettyTable

while True:
    print("\n")

    print("OS info")
    print(" OS type:", os.name)
    print(" OS version:", platform.platform(), platform.release())
    print(" OS architecture:", platform.machine())
    print(" Server name:", platform.node())
    hostname = socket.gethostname()
    print(" Server hostname:", hostname)
    ipAddr = socket.gethostbyname(hostname)
    print(" Server ip address:", ipAddr)
    print()

    print("Memory usage")
    vm = psutil.virtual_memory()
    memory_table = PrettyTable(["Total", "Used", "Available", "Percentage"])
    memory_table.add_row([vm.total, vm.used, vm.available, vm.percent])
    print(memory_table)
    print()

    print("Disk usage")
    disk = psutil.disk_usage('/')
    disk_table = PrettyTable(["Total", "Used", "Available", "Percentage"])
    disk_table.add_row([disk.total, disk.used, disk.free, disk.percent])
    print(disk_table)
    print()

    print("Top 10 processes with highest cpu usage")
    processes = []
    # get cpu usage of user´s processes
    for pid in psutil.pids()[-200:]:
        try:
            proc = psutil.Process(pid)
            proc.cpu_percent()
            processes.append(proc)
        except Exception as e:
            pass
    # sort by cpu percent
    top = {}
    time.sleep(.1)
    for proc in processes:
        top[proc] = proc.cpu_percent() / psutil.cpu_count()
    top10 = sorted(top.items(), key=lambda x: x[1])[-10:]
    top10.reverse()
    process_table = PrettyTable(["Pid", "Name", "Status", "CPU Usage", "Threads", "Memory"])
    for proc, cpu_usage in top10:
        # while fetching processes some may exit, so we need to handle potential errors
        try:
            with proc.oneshot():

                process_table.add_row([
                    str(proc.pid),
                    proc.name(),
                    proc.status(),
                    f'{cpu_usage:.2f}%',
                    proc.num_threads(),
                    f'{proc.memory_info().rss/1e6:.3f}'
                ])
        except Exception as e:
            pass
    print(process_table)

    time.sleep(1)