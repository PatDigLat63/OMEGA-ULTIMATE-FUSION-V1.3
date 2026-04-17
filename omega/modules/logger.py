"""Logger module – display and tail the OMEGA audit / application log."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.table import Table

from omega.modules.base import BaseModule

console = Console()

DEFAULT_LOG_PATH = Path.home() / ".omega" / "omega.log"


class LoggerModule(BaseModule):
    """Display the OMEGA application log and configure log verbosity."""

    name = "logger"
    description = "View the OMEGA application log and configure log verbosity"

    def run(self) -> None:
        log_path = Path(self.config.get("log_path", DEFAULT_LOG_PATH))
        log_path.parent.mkdir(parents=True, exist_ok=True)

        console.print(f"[bold cyan]Logger[/bold cyan] – {log_path}\n")

        if not log_path.exists() or log_path.stat().st_size == 0:
            console.print("[dim]No log entries found.[/dim]")
            return

        lines = log_path.read_text(encoding="utf-8").splitlines()
        tail = self.config.get("tail_lines", 50)
        lines = lines[-tail:]

        table = Table(title=f"Last {len(lines)} log entries", border_style="blue", show_lines=False)
        table.add_column("Line", style="dim", no_wrap=True, width=6)
        table.add_column("Entry", style="white")

        for i, line in enumerate(lines, start=1):
            style = "bold red" if "ERROR" in line else ("yellow" if "WARNING" in line else "white")
            table.add_row(str(i), f"[{style}]{line}[/{style}]")

        console.print(table)
