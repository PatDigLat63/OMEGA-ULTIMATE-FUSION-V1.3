"""System-Info module – displays live system resource statistics."""

from __future__ import annotations

import platform

import psutil
from rich.console import Console
from rich.table import Table

from omega.modules.base import BaseModule

console = Console()


class SystemInfoModule(BaseModule):
    """Show CPU, memory, disk and network statistics for the host machine."""

    name = "system-info"
    description = "Display live system resource statistics (CPU / RAM / disk / network)"

    def run(self) -> None:
        cpu_percent = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net = psutil.net_io_counters()

        table = Table(title="🖥  System Information", border_style="cyan")
        table.add_column("Metric", style="bold yellow", no_wrap=True)
        table.add_column("Value", style="white")

        table.add_row("OS", platform.platform())
        table.add_row("Python", platform.python_version())
        table.add_row("CPU Usage", f"{cpu_percent:.1f}%")
        table.add_row("CPU Cores (logical)", str(psutil.cpu_count(logical=True)))
        table.add_row("RAM Total", _fmt_bytes(mem.total))
        table.add_row("RAM Used", f"{_fmt_bytes(mem.used)} ({mem.percent:.1f}%)")
        table.add_row("RAM Available", _fmt_bytes(mem.available))
        table.add_row("Disk Total", _fmt_bytes(disk.total))
        table.add_row("Disk Used", f"{_fmt_bytes(disk.used)} ({disk.percent:.1f}%)")
        table.add_row("Disk Free", _fmt_bytes(disk.free))
        table.add_row("Net Bytes Sent", _fmt_bytes(net.bytes_sent))
        table.add_row("Net Bytes Recv", _fmt_bytes(net.bytes_recv))

        console.print(table)


def _fmt_bytes(n: int) -> str:
    value: float = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024:
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{value:.2f} PB"
